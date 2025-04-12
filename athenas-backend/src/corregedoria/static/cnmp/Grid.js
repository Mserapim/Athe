Ext._define('corregedoria.cnmp.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cnmp.Window',

    configOrderToolBar: ['add', 'edit', 'remove','-','search', 'statusFilter','-','sendInformation','-','->','adminMenu'],

    removeAllFilterPropertyLocal: function(reload) {
        var oldFilter = this.getFilter();

        oldFilter.forEach(
            function(item) {
                this.removeFilterProperty(item.property, item.stage, false);
            },
            this
        );
        // this.getStore().load();
    },

    applyStatus: function(status) {
        this.removeFilterProperty('status', 1000, false);
        this.addFilterProperty('status', status, 1000);
    },

    getStatusFilterAction: function() {
        if(!this._statusFilterAction){
            this._statusFilterAction = new Ext.Button({
                xtype: 'button',
                text: 'Exibir',
                iconCls: 'icon-crgmpe icon-crgmpe-find',
                menu: [
                    {
                        text: 'Pendentes de envio',
                        iconCls: 'icon-crgmpe icon-crgmpe-waiting',
                        scope: this,
                        handler: function() { this.applyStatus(1);}
                    },
                    {
                        text: 'Enviados com sucesso',
                        iconCls: 'icon-crgmpe icon-crgmpe-confirmed',
                        scope: this,
                        handler: function() { this.applyStatus(2);}
                    },
                    {
                        text: 'Envios com pendencias',
                        iconCls: 'icon-crgmpe icon-crgmpe-warn',
                        scope: this,
                        handler: function() { this.applyStatus(3);}
                    },
                    {
                        text: 'Envios com erros',
                        iconCls: 'icon-crgmpe icon-crgmpe-exclamation-red',
                        scope: this,
                        handler: function() { this.applyStatus(4);}
                    },
                    {
                        text: 'Envios com falha',
                        iconCls: 'icon-crgmpe icon-crgmpe-exclamation-black',
                        scope: this,
                        handler: function() { this.applyStatus(5);}
                    },
                ]
            });
        }
        return this._statusFilterAction;
    },

    sendInformationEmployee: function() {
        selected = this.getSelectionModel().getSelected();

        if(selected) {
            
            Ext.Msg.show({
                title: 'Envio de informações - SCMMP',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Tem certeza que deseja enviar os dados ao SCMMP?',
                scope: this,
                fn: function(btn) {
                    if(btn == 'no')
                        return;

                    var mask = new Ext.LoadMask(this.getEl(), {msg: 'Enviando ...'});
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction(this.factoryRestful().resource, 'send_information'),
                        callback: function() {
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Enviar',
                                msg: rst.message,
                                icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                            if (rst.success == true) {
                                core.invokeCallback((this.callback || {}).success);
                            }
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Enviar',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: {pk: selected.get('pk')},
                    });
                }
            });
        } else
            Ext.Msg.show({
                title: 'Envio de informações',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione o membro que deseja enviar as informações.'
            });

    },

    getSendInformationAction: function() {
        if(!this._sendInformation){
            this._sendInformation = new Ext.Button({
                xtype: 'button',
                text: 'Enviar',
                iconCls: 'icon-crgmpe icon-crgmpe-up-graph',
                scope: this,
                handler: function() { this.sendInformationEmployee();}
            });
        }
        return this._sendInformation;
    },

    getAdminMenuAction: function() {
        if(!this._adminMenuAction){
            this._adminMenuAction = new Ext.Button({
                xtype: 'button',
                text: 'Administração',
                iconCls: 'icon-crgmpe icon-crgmpe-tool',
                menu: [
                    {
                        text: 'Criar para todos membros ativos',
                        iconCls: 'icon-crgmpe icon-crgmpe-waiting',
                        scope: this,
                        handler: function() { this.addAllEmployee();}
                    },
                ]
            });
        }
        return this._adminMenuAction;
    },

    addAllEmployee: function() {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Gerando ...'});
        mask.show();
        Ext.Ajax.request({
            scope: this,
            url: core.callAction(this.factoryRestful().resource, 'bulk_generate'),
            callback: function() {
                mask.hide();
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Salvar',
                    msg: rst.message,
                    icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
                if (rst.success == true) {
                    core.invokeCallback((this.callback || {}).success);
                }
            },
            failure: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Salvar',
                    msg: rst.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            params: [],
        });
    },


    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 50, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Membro', dataIndex: 'employee_unicode', id: 'autoExpandColumn', }
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cnmp.Restful',
    'corregedoria.cnmp.Grid'
);
