# pylint: skip-file

class ZbxMaintenance(Zbx):
    '''zabbix module for maintenance'''
    zbx_type = 'maintenance'
    zbx_id = 'maintenanceid'

    def __init__(self,
                 zbx_server,
                 zbx_user,
                 zbx_password,
                 zbx_debug,
                 zbx_sslverify,
                 params):
        '''constructor for zbx module'''
        super(ZbxMaintenance, self).__init__(zbx_server,
                                             zbx_user,
                                             zbx_password,
                                             self.zbx_type,
                                             self.zbx_id,
                                             zbx_debug,
                                             zbx_sslverify)

        self.name = params.get('name', None)
        self.description = params.get('description', None)
        self.start_time = params.get('start_time', None)
        self.duration = params.get('duration', None)
        self.data_collection = params.get('data_collection', None)
        self.hosts = params.get('hosts', None)
        self.hostgroups = params.get('hostgroups', None)

    def list(self, query=None):
        ''' list '''
        if query:
            query = query
        elif self.name == None:
            query = {'search': {'name': ''}}
        else:
            query = {'search': {'name': self.name}}

        query['output'] = 'extend'
        query['selectGroups'] = 'groupids'
        query['selectHosts'] = 'hostids'
        query['selectTimeperiods'] = 'extend'

        rval = self._list(query)

        return rval

    def params(self):
        '''return a dictionary that zabbix expects of the params passed'''
        duration = ZbxMaintenance.get_active_till(self.duration)
        period = self.start_time + duration
        params = {'groupids': None,
                  'hostids': None,
                  'name': self.name,
                  'description': self.description,
                  'active_since': self.start_time,
                  'active_till': period,
                  'timeperiods': [{'start_time': self.start_time, 'period': duration}],
                  'maintenance_type': ZbxMaintenance.get_maintenance_type(self.data_collection)
                 }
        if self.hostgroups:
            params['groupids'] = [Hostgroup.get_host_group_id_by_name(self.zbx, hostgroup) \
                                  for hostgroup in self.hostgroups]
        if self.hosts:
            params['hostids'] = [Host.get_host_id_by_name(self.zbx, host) for host in self.hosts]

        return ZbxMaintenance.clean_params(params)

    def delete(self, mids):
        ''' delete '''
        return self._delete(mids)

    def create(self):
        ''' create '''
        return self._create(self.params())

    def update(self, differences):
        ''' update '''
        return self._update(differences)

    @staticmethod
    def convert_epoch(inval):
        '''convert epoch to datetime'''
        return datetime.datetime.fromtimestamp(int(inval)).strftime('%c')

    @staticmethod
    def get_maintenance_type(invar):
        '''determine maintenance type'''
        if not invar:
            return 1
        return 0

    @staticmethod
    def get_active_till(duration):
        ''' hours to seconds '''
        return duration * 60

    @staticmethod
    def compare_epochs_no_seconds(inv1, inv2):
        '''zabbix times don't include seconds'''
        dt1 = datetime.datetime.fromtimestamp(int(inv1))
        dt2 = datetime.datetime.fromtimestamp(int(inv2))
        if dt1.year == dt2.year and dt1.day == dt2.day and dt1.hour == dt2.hour and dt1.minute == dt2.minute:
            return True

        return False

    # pylint: disable=too-many-branches,too-many-statements,too-many-return-statements
    @staticmethod
    def run_ansible(params):
        '''perform the logic and return results'''
        rval = {'state': params['state']}
        zbx = ZbxMaintenance(params['zbx_server'],
                             params['zbx_user'],
                             params['zbx_password'],
                             params['zbx_debug'],
                             params['zbx_sslverify'],
                             params)

        content = zbx.list()

        if params['state'] == 'list':
            ########
            # List
            ########
            rval['changed'] = False
            for maintenance in content['result']:
                # be nice to user and return intelligible time stamps
                maintenance['active_till'] = ZbxMaintenance.convert_epoch(maintenance['active_till'])
                maintenance['active_since'] = ZbxMaintenance.convert_epoch(maintenance['active_since'])
            rval['results'] = content['result']
            return rval

        elif params['state'] == 'absent':
            ########
            # Absent
            ########
            if not ZbxMaintenance.exists(content):
                rval['changed'] = False
                rval['results'] = []
            else:
                content = zbx.delete([content['result'][0][ZbxMaintenance.zbx_id]])
                rval['changed'] = True
                rval['results'] = content['result']

            return rval

        elif params['state'] == 'present':
            ########
            # Create
            ########
            if not ZbxMaintenance.exists(content):
                content = zbx.create()
                rval['changed'] = True
                if content.has_key('error'):
                    rval['failed'] = True
                    rval['error'] = content['error']
                else:
                    rval['results'] = content['result']

                return rval

            ########
            # Update
            ########
            differences = {}
            zab_results = content['result'][0]
            params = zbx.params()
            for key, value in params.items():
                if key == 'groupids':
                    if zab_results.has_key('groups'):
                        zab_group_ids = [group['groupid'] for group in zab_results['groups']]
                        if set(zab_group_ids) != set(value):
                            differences[key] = value
                    else:
                        differences[key] = value

                elif key == 'hostids':
                    if zab_results.has_key('hosts'):
                        zab_host_ids = [host['hostid'] for host in zab_results['hosts']]
                        if set(zab_host_ids) != set(value):
                            differences[key] = value
                    else:
                        differences[key] = value

                elif key == 'timeperiods':
                    # timeperiods is an array of times; We are going to only check the first timeperiod
                    for t_key, t_value in value[0].items():
                        if str(zab_results[key][0][t_key]) != str(t_value):
                            differences[key] = value
                            break
                elif key in ['active_since', 'active_till']:
                    if not ZbxMaintenance.compare_epochs_no_seconds(zab_results[key], value):
                        differences[key] = value

                elif zab_results[key] != value and zab_results[key] != str(value):
                    differences[key] = value

            if not differences:
                rval['changed'] = False
                for maintenance in content['result']:
                    # be nice to user and return intelligible time stamps
                    maintenance['active_till'] = ZbxMaintenance.convert_epoch(maintenance['active_till'])
                    maintenance['active_since'] = ZbxMaintenance.convert_epoch(maintenance['active_since'])
                rval['results'] = content['result']
                return rval

            # We have differences and need to update
            differences[ZbxMaintenance.zbx_id] = zab_results[ZbxMaintenance.zbx_id]
            differences['hostids'] = params.get('hostids', [])
            differences['groupids'] = params.get('groupids', [])
            differences['active_since'] = params.get('active_since', [])
            differences['active_till'] = params.get('active_till', [])

            content = zbx.update(differences)
            if content.has_key('error'):
                return content

            rval['changed'] = True
            rval['results'] = content['result']
            return rval

        rval['failed'] = True
        rval['error'] = 'State UNKNWON'
        return rval
