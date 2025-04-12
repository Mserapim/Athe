Ext._define('planning.hiring.supervisor.SupervisorGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.supervisor.SupervisorWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'closesupervisor', '-', 'search', '->', 'download'],

    controllerName: undefined,

    getColumnModel: function() {
        if (!this._columnModel)
            this._columnModel = Ext._create('Ext.grid.ColumnModel', [
                Ext._create('Ext.grid.RowNumberer'),
                {
                    header: 'Fiscal',
                    dataIndex: 'employee_unicode',
                    id: 'autoExpandColumn'
                },
                {
                    header: 'Tipo',
                    dataIndex: 'kind_display',
                    width: 70
                },
                {
                    header: 'Portaria',
                    dataIndex: 'publication_document_unicode',
                    width: 170,
                    hidden: true
                },
                {
                    header: 'Início',
                    dataIndex: 'begin',
                    renderer: Ext.util.Format.dateRenderer('d/m/Y'),
                    width: 70
                },
                {
                    header: 'Fim',
                    dataIndex: 'end',
                    renderer: Ext.util.Format.dateRenderer('d/m/Y'),
                    width: 70
                },
                {
                    header: 'Observação',
                    dataIndex: 'observation',
                    hidden: true
                }
            ]);

        return this._columnModel;
    },

    getCloseSupervisorWindow: function() {
        return Ext._create('planejamento.hiring.supervisor.CloseSupervisorWindow', {
            pk_supervisor: this.getSelectionModel().getSelected().get('pk'),
            supervisorGrid: this,
            controllerName: this.controllerName
        });
    },

    closeSupervisor: function() {
        var sels = this.getSelectionModel().getSelections();

        if (sels.length > 0) {
            Ext.Ajax.request({
                scope: this,
                url: core.callAction(this.controllerName, 'check_close_action'),
                success: function(response, options) {
                    var obj = Ext.decode(response.responseText);
                    if (obj.success) {
                        this.getCloseSupervisorWindow().show();
                    } else if (!obj.success) {
                        Ext.Msg.show({
                            title: this.title,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                    }
                },
                failure: function(response, options) {
                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: response.status
                    });
                },
                params: {
                    pk: this.getSelectionModel().getSelected().get('pk'),
                },
            });
        } else {
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um registro para encerrar'
            });
        }
    },

    getClosesupervisorAction: function() {
        if (!this._closeSupervisor)
            this._closeSupervisor = Ext._create('Ext.Button', {
                text: 'Encerrar',
                iconCls: 'icon-agree icon-agree-close-supervisor',
                scope: this,
                handler: this.closeSupervisor,
            });

        return this._closeSupervisor;
    }
});

core.RestfulGrid.register(
    'planning.hiring.supervisor.SupervisorRestful',
    'planning.hiring.supervisor.SupervisorGrid'
);
