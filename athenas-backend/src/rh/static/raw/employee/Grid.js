Ext._define('rh.raw.employee.Grid', {
    extend: 'rh.raw.Grid',

    constructor: function(cfg) {
        rh.raw.employee.Grid.superclass.constructor.call(this, cfg);
    },

    getColumnModelItems: function(){
        if(!this._columnModelItems){
            this._columnModelItems = rh.raw.employee.Grid.superclass.getColumnModelItems.call(this, {});
            this._columnModelItems = this._columnModelItems.concat([
                {header: 'Servidor', dataIndex: 'servidor_unicode', width: 220, id: 'autoExpandColumn'},
                {header: 'Criado por', dataIndex: 'created_by_unicode', hidden: true, width: 120, hidden: true},
                {header: 'Criado em', dataIndex: 'created_at', hidden: true, width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true},
                {header: 'Modificado por', dataIndex: 'modified_by_unicode', hidden: true, width: 120, hidden: true},
                {header: 'Modificado em', dataIndex: 'modified_at', hidden: true, width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true},
            ]);
        }
        return this._columnModelItems;
    },

});
