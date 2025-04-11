/**
 *
 **/
Ext._define('standard.classcode.Restful', {
    extend: 'core.Restful',

    resource: 'STDClassCodeRestful',

    remote: false,

    getFields: function() {
        var fields = standard.classcode.Restful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'pk', type: 'int'},
            {name: 'slug', type: 'string'},
            {name: 'title', type: 'string'},
            {name: 'path', type: 'string'},
            {name: 'name_object', type: 'string'},
            {name: 'description', type: 'string'},
            {name: 'typeof', type: 'string'},
        ]);
    }
});
