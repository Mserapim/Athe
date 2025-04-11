/**
 *
 **/
Ext._define('engine.ControllerPermissionRestful', {
    extend: 'core.Restful',

    resource: 'ENGControllerPermissionRestful',

    getFields: function() {
        if(!this._fields)
            this._fields = engine.ControllerPermissionRestful.superclass.getFields.call(this).concat([
                {name: 'name', type: 'string'},
                {name: 'is_default', type: 'bool'},
                {name: 'manager_permission', type: 'bool'},

            ]);

        return this._fields;
    }
});
