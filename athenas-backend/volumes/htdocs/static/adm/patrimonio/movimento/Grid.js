Ext._define('adm.patrimonio.movimento.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.movimento.RestfulWindow',

    changeState: function(state) {
        var selections = this.getSelectionModel().getSelections();
        var states = {
            1: 'Mudando o estado para Aberto',
            2: 'Mudando o estado para Aguardando Recebimento',
            3: 'Mudando o estado para Recebido',
            4: 'Mudando o estado para Ciente',
            5: 'Mudando o estado para Cancelado'
        };

        if (selections.length > 0) {
            Ext.Msg.show({
                title:  'Mudando o estado do movimento',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNOCANCEL,
                msg: 'Deseja fazer alguma manifestação para a mudança de estado?',
                scope: this,
                fn: function(btn) {
                    if(btn == 'no') {
                        rest = Ext._create('adm.patrimonio.movimento.LogStatusRestful');

                        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
                        mask.show();

                        rest.manifestateStatusChange(
                            {
                                pkset: selections.map(function(row) { return row.get('pk');}),
                                status: state
                            },
                            {
                                scope: this,
                                fn: function(result) {
                                    Ext.Msg.show({
                                        title: 'Alterando estado de Movimentação.',
                                        icon: result.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                                        msg: result.message,
                                        buttons: Ext.Msg.OK
                                    });
                                }
                            },
                            {
                                scope: this,
                                fn: function(message) {
                                    Ext.Msg.show({
                                        title: 'Alterando estado de Movimentação',
                                        msg: message,
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK
                                    });
                                }
                            },
                            {
                                scope: this,
                                fn: function(result) {
                                    mask.hide();
                                    this.getStore().reload();
                                }
                            }
                        );
                    }

                    else if (btn == 'yes') {
                        Ext._create('adm.patrimonio.movimento.StatusManifestation', {
                            title: states[state],
                            params: {
                                movimentos: selections.map(function(row) {return row.get('pk');}),
                                status: state
                            },
                            callback: {
                                success: {
                                    scope: this,
                                    fn: function() {
                                        this.getStore().reload();
                                    }
                                }
                            }
                        }).show();
                    }
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Mudar estado',
                icon: Ext.Msg.WARNING,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione uma movimentação para poder mudar o estado'
            });
        }
    },

    filterStatus: function(number, checked) {
        var status__in = core.nullValue(this._filter_status__in, []);

        if(checked)
            status__in.push(number);
        else
            status__in.remove(number);

        this._filter_status__in = status__in;
        this.setFilterProperty('status__in', this._filter_status__in, 1);
    },

    getFilterMenu: function() {
        this._filter_status__in = [1, 2, 3, 4];
        this.setFilterProperty('status__in', this._filter_status__in, 1, false);

        return [
            {
                text: 'Em aberto',
                checked: this._filter_status__in.indexOf(1) >= 0,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function(btn, checked) {
                        this.filterStatus(1, checked);
                    }
                }
            },
            {
                text: 'Aguardando recebimento',
                checked: this._filter_status__in.indexOf(2) >= 0,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function(btn, checked) {
                        this.filterStatus(2, checked);
                    }
                }
            },
            {
                text: 'Recebidos',
                checked: this._filter_status__in.indexOf(3) >= 0,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function(btn, checked) {
                        this.filterStatus(3, checked);
                    }
                }
            },
            {
                text: 'Validados',
                checked: this._filter_status__in.indexOf(4) >= 0,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function(btn, checked) {
                        this.filterStatus(4, checked);
                    }
                }
            },
            {
                text: 'Autorizado',
                checked: this._filter_status__in.indexOf(6) >= 0,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function(btn, checked) {
                        this.filterStatus(6, checked);
                    }
                }
            },
            {
                text: 'Cancelados',
                checked: this._filter_status__in.indexOf(5) >= 1,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function(btn, checked) {
                        this.filterStatus(5, checked);
                    }
                }
            },
            '-',
            {
                text: 'Por Nota de Entrada',
                scope: this,
                handler: this.filterNotaEntrada
            }
        ];
    },

    filterNotaEntrada: function() {
        Ext._create('core.GridSelectWindow', {
            rest: 'adm.patrimonio.entrada.Restful',
            title: 'Selecione um entrada para filtrar',
            region: 'center',
            width: Ext.getBody().getBox().width * 0.9,
            height: Ext.getBody().getBox().height * 0.9,
            callback: {
                scope: this,
                fn: function(instance) {
                    if(instance)
                        this.setFilterProperty("itens__item_entrada__nota", instance.get('pk'), 1004);
                    else
                        this.removeFilterProperty('itens__item_entrada__nota', 1004);
                }
            }
        }).show();
    },

    termoReport: function() {
        var selection = this.getSelectionModel().getSelected();

        if (selection){

            engine.mq.Report.request({
                report: '/to/mpe/adm/patrimonio/termo_responsabilidade',

                el: this.getEl(),

                waitMessage: 'Gerando relatório...',

                params: {

                    outfile: 'termo_responsabilidade-' + selection.get('responsavel_destino_unicode'),

                    report_name: 'Termo de Responsabilidade - ' + selection.get('responsavel_destino_unicode'),

                    movimento: selection.get('pk'),

                }

            });

        } else {

            Ext.Msg.show({

                title: 'Atenção',

                icon: Ext.Msg.INFO,

                buttons: Ext.Msg.OK,

                msg: 'Selecione pelo menos um item.'

            });
        }
    },

    authorize: function() {
        var selection = this.getSelectionModel().getSelections();
        var rest = this.factoryRestful();

        if(selection.length > 0)
            Ext.Msg.show({
                title: 'Autorizar Movimentações',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Tem certeza que deseja autorizar as movimentações selecionadas?',
                scope: this,
                fn: function(btn) {
                    if(btn == 'no') return;

                    var mask = new Ext.LoadMask(this.getEl());

                    mask.show();
                    rest.doRequest(
                        rest.getRoute(
                           'authorize',
                           false,
                           'POST',
                           {
                                callback: function() {
                                    mask.hide();
                                    mask = null;
                                },
                                params: {
                                    pk__in: selection.map(
                                        function(record) {
                                            return record.get('pk');
                                        }
                                    )
                                },
                                scope: this,
                                success: function(request) {
                                    var rst = Ext.decode(request.responseText);

                                    if(rst.success)
                                        this.getStore().reload();
                                    else
                                        Ext.Msg.show({
                                            title: 'Autorizando movimentação',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK,
                                            msg: rst.message
                                        });
                                }
                           }
                        )
                    );
                }
            });
        else
            Ext.Msg.show({
                title: 'Autorizar Movimentações',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione as movimentações que deseja autorizar.'
            });
    },

    getAuthorizationButton: function() {
        if(!this._authorizationButton) {
            this._authorizationButton = Ext._create('Ext.Button', {
                text: 'Autorizar',
                scope: this,
                disabled: true,
                iconCls: 'icon-patrimonio icon-pat-autorizado',
                handler: this.authorize
            });
        }

        return this._authorizationButton;
    },

    bulkSend: function (params) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Notificando...'});
        mask.show();

        Ext.Ajax.request({
            url: core.callAction('PATNotification', 'bulk_send'),
            params: params,
            scope: this,
            success: function(response, options) {
                var result = Ext.decode(response.responseText);

                if (result.success) {
                    this.getStore().reload();
                    return;
                }

                Ext.Msg.show({
                    title: 'Notificação',
                    msg: result.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            failure: function(response, options) {
                Ext.Msg.show({
                    title: 'Notificação',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            callback: function() {
                mask.hide();
            },
        });
    },

    notify: function() {
        var selections = this.getSelectionModel().getSelections();

        if (!selections.length) {
            Ext.Msg.show({
                title: 'Notificação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: '\
                    Selecione uma ou mais movimentações para notificar \
                    os responsáveis pelo recebimento.'
            });
            return;
        }

        var notified_movements = [];
        selections.forEach(function(row) {
            if (row.get('has_notifications')) {
                notified_movements.push(row.get('identificacao'));
            }
        });

        var msg = 'Tem certeza de que deseja prosseguir com a operação?';
        if (notified_movements.length) {
            msg = 'Os movimentos a seguir já possuem notificação:' +
                '<br>' +
                notified_movements.join(', ') +
                '<br><br>' +
                'Tem certeza de que deseja prosseguir com a operação?';
        }

        Ext.Msg.show({
            title: 'Notificação',
            msg: msg,
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if (btn === 'no') {
                    return;
                }
                this.bulkSend({
                    pkset: selections.map(function(row) {
                        return row.get('pk');
                    })
                });
            }
        });
    },

    getNotifyButton: function() {
        if (!this._notifyButton) {
            this._notifyButton = Ext._create('Ext.Button', {
                text: 'Notificar',
                tooltip: 'Envia um comunicado para o responsável pelo recebimento do bem',
                scope: this,
                iconCls: 'icon-diarias icon-ocorrencia',
                handler: this.notify
            });
        }

        return this._notifyButton;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = adm.patrimonio.movimento.Grid.superclass.getToolbar.call(this, cfg);

            this._toolbar.insert(4, '-');
            this._toolbar.insert(4, {
                text: 'Termo',
                scope: this,
                iconCls: 'icon-patrimonio icon-pat-nota',
                handler: this.termoReport
            });

            this._toolbar.insert(4, '-');
            this._toolbar.insert(4, this.getAuthorizationButton());

            this._toolbar.insert(4, '-');
            this._toolbar.insert(4, {
                text: 'Mudar estado',
                iconCls: 'icon-patrimonio icon-pat-nota-baixa-transferencia',
                menu: [
                    {
                        text: 'Aberto',
                        scope: this,
                        handler: function() {this.changeState(1); },
                        iconCls: 'icon-patrimonio icon-pat-aberto'
                    },
                    {
                        text: 'Aguardando Recebimento',
                        scope: this,
                        handler: function() {this.changeState(2); },
                        iconCls: 'icon-patrimonio icon-pat-aguardando-recebimento'
                    },
                    {
                        text: 'Recebido',
                        scope: this,
                        handler: function() {this.changeState(3); },
                        iconCls: 'icon-patrimonio icon-pat-concluido'
                    },
                    '-',
                    {
                        text: 'Ciente',
                        scope: this,
                        handler: function() {this.changeState(4); },
                        iconCls: 'icon-patrimonio icon-pat-ciencia'
                    },
                    '-',
                    {
                        text: 'Cancelado',
                        scope: this,
                        handler: function() {this.changeState(5); },
                        iconCls: 'icon-patrimonio icon-pat-cancelado'
                    }
                ]
            });
            this._toolbar.insert(5, this.getNotifyButton());
        }

        return this._toolbar;
    },

    getColumnModel: function () {
        if (!this._columnModel) {
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 70,
                        menuDisabled: true,
                        renderer: adm.daily.rendererIconGrid
                    },
                    {
                        header: 'Chave',
                        dataIndex: 'id',
                        width: 85,
                        hidden: true,
                    },
                    {
                        header: 'Id',
                        dataIndex: 'identificacao',
                        width: 85
                    },
                    {
                        header: 'Origem',
                        dataIndex: 'origem_unicode',
                        width: 220,
                        hidden: true
                    },
                    {
                        header: 'Destino',
                        dataIndex: 'destino_unicode',
                        id: 'autoExpandColumn'
                    },
                    {
                        header: 'Resp. Entrega',
                        dataIndex: 'movimentado_por_unicode',
                        width: 120
                    },
                    {
                        header: 'Resp. Recebimento',
                        dataIndex: 'recebido_por_unicode',
                        width: 120
                    },
                    {
                        header: 'Validados por',
                        dataIndex: 'validado_por_unicode',
                        // id: 'autoExpandColumn'
                        width: 120
                    },
                    {
                        header: 'Autorizado',
                        dataIndex: 'autorizado',
                        width: 180,
                        renderer: function(value) {
                            return value.join(', ');
                        }
                    }
                ]
            );
        }

        return this._columnModel;
    },

    processPermissions: function(cfg) {
        if(cfg.can_authorize)
            this.getAuthorizationButton().enable();
    },

    constructor: function(cfg) {
        adm.patrimonio.movimento.Grid.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            render: function(panel) {
                var rest = this.factoryRestful();

                rest.doRequest(
                    rest.getRoute(
                       'perms',
                       false,
                       'GET',
                       {
                            scope: this,
                            success: function(request) {
                                this.processPermissions(Ext.decode(request.responseText));
                            }
                       }
                    )
                );
            }
        });
    }
});
