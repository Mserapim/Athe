/**
 *
 **/
Ext._define('engine.ControllerRestful', {
    extend: 'core.Restful',

    resource: 'ENGControllerRestful',

    getFields: function() {
        if(!this._fields)
            this._fields = engine.ControllerRestful.superclass.getFields.call(this).concat([
                {name: 'icons', type: 'auto'},
                {name: 'icon', type: 'string'},
                {name: 'title', type: 'string'},
                {name: 'controller', type: 'string'},
                {name: 'application', type: 'int'},
                {name: 'application_unicode', type: 'string'},
                {name: 'application_active', type: 'bool'},
                {name: 'active', type: 'bool'},
                {name: 'module', type: 'string'},
                {name: "created_by",type: "int",useNull: true},
                {name: "created_by_unicode",type: "string"},
                {name: 'modified_by', type: 'int',useNull: true},
                {name: "modified_by_unicode",type: "string"},
            ]);

        return this._fields;
    }
});
