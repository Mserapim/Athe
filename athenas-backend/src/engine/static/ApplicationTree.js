/**
 *
 **/
Ext._define('engine.ApplicationTree', {
    'extend': 'core.RestfulTree',

    'restWindow': 'engine.ApplicationWindow',

    'folderIndexField': 'father',

    'getToolbar': function(cfg) {
        if(!this._toolbar) {
            this._toolbar = engine.ApplicationTree.superclass.getToolbar.call(this, cfg);

            this._toolbar.items.each(
                function(button) {
                    button.text = '';
                }
            )
        }

        return this._toolbar;
    }
});
