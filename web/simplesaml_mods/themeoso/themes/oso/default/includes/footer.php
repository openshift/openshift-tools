<?php
if(!empty($this->data['htmlinject']['htmlContentPost'])) {
    foreach($this->data['htmlinject']['htmlContentPost'] AS $c) {
        echo $c;
    }
}
?>
    </div><!-- #content -->
    <div id="footer">
        <hr />
                <img src="/<?php echo $this->data['baseurlpath']; ?>resources/icons/ssplogo-fish-small.png" alt="Small fish logo"  class="float_right" />
        You are accessing a service that is for use only by authorized users.  If you do not have authorization, discontinue use at once.
                <br class="clear_right" />
    </div><!-- #footer -->

</div><!-- #wrap -->

</body>
</html>
