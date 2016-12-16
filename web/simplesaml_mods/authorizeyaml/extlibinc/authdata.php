<?PHP

class AuthData
{
    private $data;
    public function __construct($yaml_authdata_path)
    {
        $this->data = yaml_parse_file($yaml_authdata_path);
        // sanity check what we found
        if (!$this->data)
        {
            $this->data = array();
        }
        if (!array_key_exists('groups', $this->data))
        {
            $this->data['groups'] = array();
        }
        if (!array_key_exists('members', $this->data))
        {
            $this->data['members'] = array();
        }
        if (!array_key_exists('default_roles', $this->data))
        {
            $this->data['default_roles'] = array();
        }
        if (!array_key_exists('resources', $this->data))
        {
            $this->data['resources'] = array();
        }
    }

    public function getGroups($user)
    {
        $retval = array();
        foreach ($this->data['groups'] as $group)
        {
            foreach ($group['members'] as $member)
            {
                if ($user == $member)
                {
                    array_push($retval, $group['name']);
                }
            }
            if (in_array($user, $group['members']))
            {
                array_push($retval, $group['name']);
            }
        }
        return $retval;
    }

    public function getRoles($resource, $user, $groups)
    {
        if (is_null($resource))
            return null;
        $roles = array_key_exists('roles', $resource) ? $resource['roles'] : $this->data['default_roles'];
        foreach ($roles as $role)
        {
            if (array_key_exists('members', $role) && array_search($user, $role['members']))
            {
                return $role['name'];
            }
            if (array_key_exists('groups', $role) && count(array_uintersect($groups, $role['groups'], 'strcmp')))
            {
                return $role['name'];
            }
        }
        return null;
    }
    public function getResourceIds()
    {
        $retval = array();
        foreach ($this->data['resources'] as $resource)
        {
            array_push($retval, $resource['id']);
        }
        return $retval;
    }
    public function getResource($id)
    {
        if (is_null($id) || empty($id))
            return null;
        foreach ($this->data['resources'] as $resource)
        {
            if ($resource['id'] == $id)
                return $resource;
        }
        return null;
    }
}

