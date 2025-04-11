Ext._define('raf.adjustment.dataadjustment.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.adjustment.dataadjustment.Window',

    configOrderToolBar: ['add', 'remove', '->', 'response', 'accept', 'requestInformation', 'reject', 'searchProcessNumber', 'showAutoReference'],

    removeItems: function(record, cfg) {
        var selected = this.getSelectionModel().getSelected();
        if (selected.data.situation == 4) {
            Ext.Msg.show({
                title: 'Ajuste de Atividade',
                msg: 'Solicitação cancelada, remoção de itens não permitida.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        } else {
            if (selected.data.situation != 5) {
                Ext.Msg.show({
                    title: 'Ajuste de Atividade',
                    msg: 'Solicitação já enviada para análise, remoção de itens não permitida.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
            if (selected.data.situation == 5) {
                raf.adjustment.dataadjustment.Grid.superclass.removeItems.call(this, record, cfg);
            }
        }
    },

    createItem: function(values) {
        values.activity = this.params.activity;
        if (this.params.adjustmentsituation == 4) {
            Ext.Msg.show({
                title: 'Ajuste de Atividade',
                msg: 'Solicitação cancelada, remoção de itens não permitida.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        } else {
            if (this.params.adjustmentsituation != 5) {
                Ext.Msg.show({
                    title: 'Ajuste de Atividade',
                    msg: 'Solicitação já enviada para análise, adição de novos item não permitida.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
            if (this.params.adjustmentsituation == 5) {
                raf.adjustment.dataadjustment.Grid.superclass.createItem.call(this, values);
            }
        }
    },

    action: function(var_dataadjustment, var_activityadjustment, var_situation, var_answer) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Realizando análise da ajuste...'});
        mask.show();
        rest.action(
            {
                dataadjustment_list: var_dataadjustment,
                activityadjustment: var_activityadjustment,
                situation: var_situation,
                answer: var_answer,
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.getStore().load({});
                        Ext.Msg.show({
                            title: 'Análise da Solcitação de Ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Análise da Solcitação de Ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Análise da Solcitação de Ajuste',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getShowAutoReferenceAction: function() {
        if(!this._showAutoReference){
            this._showAutoReference = new Ext.Button({
                xtype: 'button',
                text: 'Ver Documentos',
                iconCls: 'icon-core icon-core-reports',
                scope: this,
                handler: function() {
                    Ext._create('raf.autoreference.DetailWindow', {
                        params: {
                            activity: this.params.activity,
                        }
                    }).show();
                }
            });
        }
        return this._showAutoReference;
    },

    getAcceptAction: function() {
        if(!this._accept){
            this._accept = new Ext.Button({
                xtype: 'button',
                text: 'Deferir',
                iconCls: 'icon-core icon-core-success',
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelections();
                    if(selected.length > 0) {
                        Ext.Msg.show({
                            title: 'Deferir solicitação',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            msg: 'Tem certeza que deseja <b>DEFERIR</b> o(s) item(ns) selecionado(s)?',
                            scope: this,
                            fn: function(btn) {
                                if(btn == 'no') return;
                                this.action(selected.map(
                                        function(data) {
                                            if ([0, 1].indexOf(data.get('situation')) >= 0) {
                                                return data.get('pk');
                                            } else {
                                                return 0;
                                            }
                                        }
                                    ).toString(), this.params.activityadjustment, 2, 'Item deferido conforme solicitação.');
                            }
                        });
                    } else {
                        Ext.Msg.show({
                            title: 'Deferir solicitação',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            msg: 'Tem certeza que deseja <b>DEFERIR TODOS</b> os itens?',
                            scope: this,
                            fn: function(btn) {
                                if(btn == 'no') return;
                                this.action(0, this.params.activityadjustment, 2, 'Item deferido conforme solicitação.');
                            }
                        });
                    }
                }
            });
        }
        return this._accept;
    },

    getRequestInformationAction: function() {
        if(!this._requestInformation){
            this._requestInformation = new Ext.Button({
                xtype: 'button',
                text: 'Solicitar mais informações',
                iconCls: 'icon-core icon-core-report-edit',
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelected();
                    if(selected) {
                        if ([0, 1, 5].indexOf(selected.data.situation) >= 0) {
                            // this.openAdjustmentCommunicationWindow(selected);
                            this.openAnswerWindow(selected, 1);
                        } else {
                            Ext.Msg.show({
                                title: 'Ajuste de Atividade',
                                msg: 'Solicitação já enviada para análise, remoção de itens não permitida.',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    } else {
                        Ext.Msg.show({
                            title: 'Ajuste de Atividade',
                            msg: 'Selecione um item em análise para solicitar não informações.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                }
            });
        }
        return this._requestInformation;
    },

    getRejectAction: function() {
        if(!this._reject){
            this._reject = new Ext.Button({
                xtype: 'button',
                text: 'Indeferir',
                iconCls: 'icon-core icon-core-error',
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelections();
                    if(selected.length == 0) {
                        activityadjustment = this.params.activityadjustment;
                    }
                    list = selected.map(
                            function(data) {
                                if ([0, 1].indexOf(data.get('situation')) >= 0) {
                                    return data.get('pk');
                                } else {
                                    return 0;
                                }
                            }).toString();
                    Ext._create('raf.adjustment.dataadjustment.RejectWindow', {
                        modal: true,
                        values: {
                            activityadjustment: this.params.activityadjustment,
                            dataadjustment_list: list,
                            situation: 3,
                        },
                        callback: {
                            success: {
                                scope: this,
                                fn: function(instance) {
                                    core.invokeCallback((this.callback || {}).success);
                                    this.getStore().load({});
                                }
                            }
                        }
                    }).show();
                }
            });
        }
        return this._reject;
    },

    getSearchProcessNumberAction: function() {
        if(!this._searchProcessNumber){
            this._searchProcessNumber = new Ext.Button({
                xtype: 'button',
                text: 'Pesquisar por número',
                iconCls: 'icon-core icon-core-select',
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelected();
                    var var_params = { };
                    if(selected) {
                        var_params = {
                            'process_number': selected.data.process_number_formatted,
                            'source': selected.data.source,
                        };
                    }
                    Ext._create('raf.searchprocessnumber.SearchProcessNumberWindow', {
                        params: var_params,
                    }).show();
                }
            });
        }
        return this._searchProcessNumber;
    },

    getResponseAction: function() {
        if(!this._response){
            this._response = new Ext.Button({
                xtype: 'button',
                text: 'Responder',
                iconCls: 'icon-core icon-core-report-edit',
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelected();
                    if(selected) {
                        if ([1, 5].indexOf(selected.data.situation) < 0) {
                            Ext.Msg.show({
                                title: 'Ajuste de Atividade',
                                msg: 'Solicitação já enviada para análise, aguarde análise para envio de mais informações.',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        } else {
                            this.openAnswerWindow(selected, 0);
                        }
                    } else {
                        Ext.Msg.show({
                            title: 'Ajuste de Atividade',
                            msg: 'Selecione um item em análise para respondê-lo.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                }
            });
        }
        return this._response;
    },

    openAnswerWindow: function(value, var_situation) {
        Ext._create('raf.conversation.AnswerWindow', {
            modal: true,
            values: {
                conversation: value.get('conversation'),
                origin: value.get('location'),
                situation: var_situation,
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.getStore().load({});
                    }
                }
            }
        }).show();
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 26, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Operação', dataIndex: 'operation_display', width: 75, },
                    {header: 'Origem', dataIndex: 'source_display', width: 65,  align: 'center'},
                    {header: 'Número', dataIndex: 'process_number_formatted', width: 150,  align: 'center'},
                    {header: 'Data', dataIndex: 'date', width: 80,  align: 'center' },
                    {header: 'Última mensagem', dataIndex: 'conversation_last_content', width: 350,
                        renderer: function(value, metaData, record) {
                            txt = '<div ext:qtip="' + record.get('conversation_last_content') + '">' + value + '</div>';
                            return txt;
                        },
                    },
                    {header: 'Classificação Taxonômica', dataIndex: 'classification', id: 'autoExpandColumn',
                        renderer: function(value, metaData, record) {
                            txt = '<div ext:qtip="' + record.get('classification') + '">' + value + '</div>';
                            return txt;
                        },
                    },
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'raf.adjustment.dataadjustment.Restful',
    'raf.adjustment.dataadjustment.Grid'
);
