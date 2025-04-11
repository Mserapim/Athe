Ext._define('planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerGridAdmin', {
    
    extend: 'planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerGrid',

    configOrderToolBar: ['addsolicitation', 'remove', '-', 'generateOrder', 'situation', 'generateAgreement', 'rebalancing', '-', 'ask', '-', 'report', '-', 'search', 'filter', '->', 'download'],
    
    getAskAction: function () {
        if (!this._askAction)
            this._askAction = Ext._create('Ext.Button', {
                text: 'Alterar Status',
                iconCls: 'icon-core icon-core-refresh',
                scope: this,
                menu: [
                    {
                        text: 'Contratado',
                        scope: this,
                        iconCls: 'icon-core icon-core-document-arrow',
                        handler: function () {
                            this.execActionStatus(7); // MINUTE_SOLICITATION_SITUATION = 7 (Contratado)
                        }
                    },
                ]
            });

        return this._askAction;
    },

    execActionStatus: function (num) {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            Ext.Msg.show({
                title: 'Alerta',
                msg: 'Confirma alteração do contrato de '+ selected.get('situation_display')+' para Contratado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn:function(btn){
                   if (btn == 'no') return;
                    Ext.Ajax.request({
                        url: core.callAction('PHMMinuteSolicitationAction', 'update_status_minute_solicitation'),
                        scope: this,
                        params: {
                            solicitation: this.getSelectionModel().getSelections().map(
                            function (record) {
                                return record.get('pk')
                            }
                            ).join(),
                            action: num
                        },
                        success: function (response) {
                            var obj = Ext.decode(response.responseText);
                            if (obj.success)
                                this.getStore().reload();
                            else
                                Ext.Msg.show({
                                    title: 'Ocorreu um erro',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK,
                                    msg: rst.message
                                });
                        }
                    });
                }
            })
        } else {
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um pedido para alterar status.'
            });
        }
    },
});