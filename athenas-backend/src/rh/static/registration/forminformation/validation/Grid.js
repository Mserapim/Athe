Ext._define('rh.registration.forminformation.validation.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.registration.forminformation.validation.Window',

    hideItemsToolbar: ['add', 'remove', 'search'],
    hideActions: ['remove', 'copy', 'edit'],


    getConfigActionsItems: function(cfg){
        var menu = rh.registration.forminformation.validation.Grid.superclass.getConfigActionsItems.call(this, cfg);

        menu.edit.text = 'Ver Validação';

        return menu;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Validado por', dataIndex: 'validate_employee', id: 'autoExpandColumn'},
                    {header: 'Mensagem', dataIndex: 'text', width: 250, hidden: true},
                    {header: 'Estado', dataIndex: 'state_display', width: 120, hidden: false},
                    {header: 'Validado em', dataIndex: 'validated_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true},
                    {header: 'Formulário enviado por', dataIndex: 'fi_sent_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Formulário enviado em', dataIndex: 'fi_sent_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true},
                    {header: 'Formulário recebido por', dataIndex: 'fi_received_by_unicode', width: 120, sortable: true, hidden: true},
                    {header: 'Formulário recebido em', dataIndex: 'fi_received_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.registration.forminformation.validation.Restful',
    'rh.registration.forminformation.validation.Grid'
);

