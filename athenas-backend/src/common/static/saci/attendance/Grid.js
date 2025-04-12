
Ext._define('common.saci.attendance.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.saci.attendance.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'search', 'historic', '-', 'print'],
    keywordFieldMessage: 'Pesquisar',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 26, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Protocolo', dataIndex: 'protocol_unicode', width: 130},
                    {header: 'Assunto', dataIndex: 'subject', id: 'autoExpandColumn'},
                    {header: 'Iniciado em', dataIndex: 'created_at', width: 110, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {header: 'Finalizado em', dataIndex: 'signed_at', width: 110, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                ]
            );

        return this._columnModel;
    },

    getPrintAction: function() {
        if(!this._printAction){
            this._printAction = new Ext.Button({
                xtype: 'button',
                text: 'Imprimir',
                iconCls: 'icon-saci icon-saci-printer',
                scope: this,
                handler: this.printAttendance
            });
        }
        return this._printAction;
    },

    getHistoricAction: function() {
        if(!this._historicAction){
            this._historicAction = new Ext.Button({
                xtype: 'button',
                text: 'Histórico de encaminhamento',
                iconCls: 'icon-saci icon-saci-historic',
                scope: this,
                handler: this.openHistoricStepWindow
            });
        }
        return this._historicAction;
    },

    openHistoricStepWindow: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            Ext._create('common.saci.attendance.HistoricStepWindow', {
                action: 'create',
                modal: true,
                attendance: selected.get('pk'),
                callback: {
                    success: {
                        scope: this,
                        fn: function(instance) {
                            core.invokeCallback((this.callback || {}).success);
                            this.close();
                        }
                    }
                }
            }).show();
        } else {
            Ext.Msg.show({
                title: 'Histórico de encaminhamento',
                msg: 'Primeiro selecione o atendimento que deseja visualizar o histórico de encaminhamento.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }

    },

    printAttendance: function(){
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var wnd = window.open(
                '/athenas/SACIAttendanceRestful/renderer_document_to_print/?attendance=' + selected.get('pk'),
                '_to_printer',
                (new SquareScreen(0.85)).toString() + ', scrollbars=yes'
            );

            if(!wnd)
                Ext.Msg.show({
                    title: 'Preparando para imprimir',
                    msg: 'Não foi possivel preparar o documento para impressão, devido ao bloqueador de popup.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            else
                wnd.onload = wnd.print;
        }
        else {
            Ext.Msg.show({
                title: 'Imprimir Atendimento',
                msg: 'Primeiro selecione o atendimento que deseja Imprimir.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    _hasRestrictedRecords: function (record) {
        if (record instanceof Ext.Button) {
            record = undefined;
        }

        var selections = core.nullValue(
            record,
            this.getSelectionModel().getSelections()
        );

        if (!Ext.isArray(selections)) {
            selections = [selections];
        }

        var restrictedExists = false;
        selections.forEach(function (value) {
            if (!value.data.can_read) {
                restrictedExists = true;
            }
        });

        return restrictedExists;
    },

    /**
     * Método sobrescrito para se adequar ao Controle de Acesso.
     */
    updateItem: function(record) {
        if (!this.allowUpdate) {
            return;
        }

        if (this._hasRestrictedRecords(record)) {
            Ext.Msg.show({
                title: 'Classificando informação',
                msg: 'Este documento possui controle de acesso.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        } else {
            common.saci.attendance.Grid.superclass.updateItem.call(this, record);
        }
    },

    /**
     * Método sobrescrito para se adequar ao Controle de Acesso.
     */
    removeItems: function(record, cfg) {
        if (!this.allowRemove) {
            return;
        }

        if (this._hasRestrictedRecords(record)) {
            Ext.Msg.show({
                title: 'Classificando informação',
                msg: 'Este documento possui controle de acesso.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        } else {
            common.saci.attendance.Grid.superclass.removeItems.call(this, record, cfg);
        }
    }
});

core.RestfulGrid.register(
    'common.saci.attendance.Restful',
    'common.saci.attendance.Grid'
);
