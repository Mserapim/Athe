/**
 *
 **/
Ext._define('engine.ControllerPermissionGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'engine.ControllerPermissionWindow',

    getColumnModel: function() {
        var is_default_column = {
            header: 'Permissões de funcionalidade padrão',
            dataIndex: 'is_default',
            width: 70,
            renderer: toolkit.util.formatIconYesNo,
        };
        var manager_permission_column = {
            header: 'Funcionalidade gestor',
            dataIndex: 'manager_permission',
            width: 70,
            renderer: toolkit.util.formatIconYesNo,
        };
        var grid_columns = [
            Ext._create('Ext.grid.RowNumberer'),
            {header: 'Descrição', dataIndex: 'unicode', id: 'autoExpandColumn'}
        ];

        if(this.getAutoPermissionsFuncs() == 'True')
            grid_columns.push(is_default_column);
        grid_columns.push(manager_permission_column)


        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                grid_columns
            );

        return this._columnModel;
    },

    setAutoPermissionsFuncs: function(autoPermissionsFuncs) {
        this.autoPermissionsFuncs = autoPermissionsFuncs;
    },

    getAutoPermissionsFuncs: function() {
        return this.autoPermissionsFuncs;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        
        this.setAutoPermissionsFuncs(cfg.autoPermissionsFuncs);

        engine.ControllerPermissionGrid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'engine.ControllerPermissionRestful',
    'engine.ControllerPermissionGrid'
);
