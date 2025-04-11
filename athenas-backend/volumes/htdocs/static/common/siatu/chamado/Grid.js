/**
 *
 * static/siatu/chamado/Grid.js
 *
 **/

Ext._define('common.siatu.chamado.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.chamado.Window',

    keywordFieldMessage: 'Código, serviço ou problema',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Codigo', dataIndex: 'identificacao', width: 80, sortable:true},
                    {header: 'Status', dataIndex: 'icon_status', width: 130, renderer: common.siatu.rendererIconGrid},
                    {header: 'Tempo decorrido', dataIndex: 'tempo_decorrido', width: 100},
                    {header: 'Fila', dataIndex: 'fila', width: 32, sortable:true, renderer: function(value) {return (value == 0) ? '' : value;} },
                    {header: 'Fila tipo', dataIndex: 'tipo_fila', width: 125, sortable:false, renderer: function(value) {return (value == 0) ? '' : value;} },
                    {header: 'Solicitante', dataIndex: 'solicitante_username', width: 100, sortable:true},
                    {header: 'Serviço', dataIndex: 'servico_unicode', width: 150, sortable:true, id: 'autoExpandColumn',},
                ]
            );

        return this._columnModel;
    },

    changeFilter: function(status, exclude) {
        exclude = core.nullValue(exclude, false);
        this.removeFilterProperty('status_atual__status__in', undefined, false);
        this.removeFilterProperty('status_atual__status', undefined, false);
        if (status) {
            if(exclude)
                this.setFilterProperty('status_atual__status__in', [status, 12], -1);
            else
                this.setFilterProperty('status_atual__status', status, 1);
        }
        else
            this.getStore().load();
    },

    setCookie: function() {
        data = new Date();
        data.setMonth(data.getMonth() + 1);
        Ext.util.Cookies.set('siatu-chamado-filterStatus', Ext.encode(this.filterStatus), data);
    },

    toggleStatus: function(status) {
        if(this.filterStatus.indexOf(status) >= 0)
            this.filterStatus.remove(status);
        else
            this.filterStatus.push(status);

        this.setCookie();
        this.setFilterProperty('status_atual__status__in', this.filterStatus, 1000);
    },

    filterLotacao: function() {
        var wnd = Ext._create('Ext.Window', {
            title: 'Selecionar Origem do Chamado',
            modal: true,
            resizable: false,
            width: 620,
            border: false,
            buttons: [
                {
                    text: 'Limpar filtro',
                    scope: this,
                    handler: function() {
                        this.getCancelarButton().show();
                        this.setFilterProperty('solicitacao__solicitante', this.solicitante, 1000);
                        this.removeFilterProperty('solicitacao__orgao_geral_origem', 1002);
                        wnd.destroy();
                    }
                },
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();
                        if(form.getValues().orgao_geral_origem) {
                            this.getCancelarButton().hide();
                            this.removeFilterProperty('solicitacao__solicitante', undefined, false);
                            this.setFilterProperty('solicitacao__orgao_geral_origem', form.getValues().orgao_geral_origem, 1002);
                        }
                        else {
                            this.getCancelarButton().show();
                            this.setFilterProperty('solicitacao__solicitante', this.solicitante, 1000);
                            this.removeFilterProperty('solicitacao__orgao_geral_origem', 1001);
                        }
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        wnd.destroy();
                    }
                }
            ],
            items: Ext._create('Ext.form.FormPanel', {
                frame: true,
                items: [
                    Ext._create('core.fields.ComboField', {
                        fieldLabel: 'Origem',
                        hiddenName: 'orgao_geral_origem',
                        displayField: 'description',
                        // emptyText: 'Origem do documento.',
                        store: Ext._create('Ext.data.Store', {
                            proxy: Ext._create('Ext.data.HttpProxy', {
                                url: core.callAction('EDOCManage', 'work_locations')
                            }),
                            reader: Ext._create('Ext.data.JsonReader', {
                                totalProperty: 'count',
                                root: 'collection',
                                fields: [
                                    {name: 'pk', type: 'int'},
                                    {name: 'description', type: 'string'},
                                ]
                            })
                        }),
                        width: 485,
                        allowBlank: false
                    })
                ]
            })
        }).show();
    },

    filterAllLocations: function() {
        var wnd = Ext._create('Ext.Window', {
            title: 'Selecionar Origem do Chamado',
            modal: true,
            resizable: false,
            width: 620,
            border: false,
            buttons: [
                {
                    text: 'Limpar filtro',
                    scope: this,
                    handler: function() {
                        // this.getStore().removeAll();
                        // this.getStore().baseParams = {};

                        // this.addFilterProperty('status', 1, 100, false);
                        // this.addFilterProperty('pendency_address', true, 101);

                        this.removeFilterProperty('solicitacao__orgao_geral_origem', 1002);
                        wnd.destroy();
                    }
                },
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();
                        if(form.getValues().orgao_geral_origem)
                            this.setFilterProperty('solicitacao__orgao_geral_origem', form.getValues().orgao_geral_origem, 1002);
                        else {
                            this.removeFilterProperty('solicitacao__orgao_geral_origem', 1002);
                        }
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        wnd.destroy();
                    }
                }
            ],
            items: Ext._create('Ext.form.FormPanel', {
                frame: true,
                items: [

                    Ext._create('core.fields.AutocompleteField',{
                        xtype: "rest-autocompletefield",
                        width: 450,
                        fieldLabel: "Origem",
                        allowBlank: false,
                        rest: "rh.workplace.Restful",
                        name: "orgao_geral_origem",
                    })
                ]
            })
        }).show();
    },

    filterService: function() {
        var wnd = Ext._create('Ext.Window', {
            title: 'Selecionar Serviço',
            modal: true,
            resizable: false,
            width: 620,
            border: false,
            buttons: [
                {
                    text: 'Limpar filtro',
                    scope: this,
                    handler: function() {
                        this.removeFilterProperty('servico__in', [], false);
                        this.setFilterProperty('servico__in', this.filterServico, 101);
                        wnd.destroy();
                    }
                },
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();
                        var servico = form.getValues().servico;

                        core.invokeCallback(this.serviceFilterCallback || { fn: Ext.emptyFn }, servico);


                        if(form.getValues().servico) {
                            this.removeFilterProperty('servico__in', [], false);
                            this.setFilterProperty('servico__in', [form.getValues().servico], 101);

                        }
                        else {
                            this.removeFilterProperty('servico__in', [], false);
                            this.setFilterProperty('servico__in', this.filterServico, 101);
                        }
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        wnd.destroy();
                    }
                }
            ],
            items: Ext._create('Ext.form.FormPanel', {
                frame: true,
                items: [

                    Ext._create('core.fields.ComboField', {
                        rest: 'common.siatu.servico.Restful',
                        fieldLabel: 'Serviço',
                        hiddenName: 'servico',
                        name: 'servico',
                        lazyRender: true,
                        lazyInit: true,
                        displayField: 'unicode',
                        triggerAction: 'all',
                        width: 450,
                        preFilter: [
                            {
                                property: 'servico_superior__isnull',
                                value: false,
                            }
                        ]
                    })
                    // Ext._create('core.fields.AutocompleteField',{
                    //     xtype: "rest-autocompletefield",
                    //     width: 450,
                    //     fieldLabel: "Serviço",
                    //     allowBlank: false,
                    //     rest: "common.siatu.servico.Restful",
                    //     name: "servico",
                    // })
                ]
            })
        }).show();
    },

    getOpenFilter: function() {
        if(!this._open) {
            this._open = Ext._create('Ext.menu.CheckItem', {
                text: 'Aberto',
                checked: (this.filterStatus.indexOf(1) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(1);
                }
            });
        }

        return this._open;
    },

    getWaitingForCustomerServiceFilter: function() {
        if(!this._waitingForCustomerService) {
            this._waitingForCustomerService = Ext._create('Ext.menu.CheckItem', {
                text: 'Aguardando Atendimento',
                checked: (this.filterStatus.indexOf(2) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(2);
                }
            });
        }

        return this._waitingForCustomerService;
    },

    getInServiceFilter: function() {
        if(!this._inService) {
            this._inService = Ext._create('Ext.menu.CheckItem', {
                text: 'Em Atendimento',
                checked: (this.filterStatus.indexOf(3) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(3);
                }
            });
        }

        return this._inService;
    },

    getAwaitingRatingFilter: function() {
        if(!this._waitingRating) {
            this._waitingRating = Ext._create('Ext.menu.CheckItem', {
                text: 'Aguardando Avaliação',
                checked: (this.filterStatus.indexOf(4) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(4);
                }
            });
        }

        return this._waitingRating;
    },

    getTransferredFilter: function() {
        if(!this._transferred) {
            this._transferred = Ext._create('Ext.menu.CheckItem', {
                text: 'Transferido',
                checked: (this.filterStatus.indexOf(5) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(5);
                }
            });
        }

        return this._transferred;
    },

    getOutsourcedFilter: function() {
        if(!this._outsourced) {
            this._outsourced = Ext._create('Ext.menu.CheckItem', {
                text: 'Terceirizada',
                checked: (this.filterStatus.indexOf(6) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(6);
                }
            });
        }

        return this._outsourced;
    },

    getWarrantyFilter: function() {
        if(!this._warranty) {
            this._warranty = Ext._create('Ext.menu.CheckItem', {
                text: 'Garantia',
                checked: (this.filterStatus.indexOf(7) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(7);
                }
            });
        }

        return this._warranty;
    },

    getTravelFilter: function() {
        if(!this._travel) {
            this._travel = Ext._create('Ext.menu.CheckItem', {
                text: 'Viagem',
                checked: (this.filterStatus.indexOf(8) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(8);
                }
            });
        }

        return this._travel;
    },

    getCompletedFilter: function() {
        if(!this._completed) {
            this._completed = Ext._create('Ext.menu.CheckItem', {
                text: 'Concluído',
                checked: (this.filterStatus.indexOf(9) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(9);
                }
            });
        }

        return this._completed;
    },

    getWaitingForDeliveryFilter: function() {
        if(!this._waitingForDelivery) {
            this._waitingForDelivery = Ext._create('Ext.menu.CheckItem', {
                text: 'Aguardando entrega',
                checked: (this.filterStatus.indexOf(10) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(10);
                }
            });
        }

        return this._waitingForDelivery;
    },

    getUnderMaintenanceFilter: function() {
        if(!this._underMaintenance) {
            this._underMaintenance = Ext._create('Ext.menu.CheckItem', {
                text: 'Em Manutenção',
                checked: (this.filterStatus.indexOf(11) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(11);
                }
            });
        }

        return this._underMaintenance;
    },

    getNotRatedFilter: function() {
        if(!this._notRated) {
            this._notRated = Ext._create('Ext.menu.CheckItem', {
                text: 'Não Avaliado',
                checked: (this.filterStatus.indexOf(12) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.toggleStatus(12);
                }
            });
        }

        return this._notRated;
    },

    getMarkAllFilter: function() {
        if(!this._markAll) {
            this._markAll = Ext._create('Ext.menu.Item', {
                text: 'Selecionar todos',
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.getOpenFilter().setChecked(true);
                    this.getWaitingForCustomerServiceFilter().setChecked(true);
                    this.getInServiceFilter().setChecked(true);
                    this.getAwaitingRatingFilter().setChecked(true);
                    this.getTransferredFilter().setChecked(true);
                    this.getOutsourcedFilter().setChecked(true);
                    this.getWarrantyFilter().setChecked(true);
                    this.getTravelFilter().setChecked(true);
                    this.getCompletedFilter().setChecked(true);
                    this.getWaitingForDeliveryFilter().setChecked(true);
                    this.getUnderMaintenanceFilter().setChecked(true);
                    this.getNotRatedFilter().setChecked(true);

                    this.filterStatus = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
                    this.removeFilterProperty('status_atual__status__in', 1000, false);
                    this.setFilterProperty('status_atual__status__in', this.filterStatus, 1000, true);
                    this.setCookie();
                }
            });
        }

        return this._markAll;
    },

    getUnmarkAllFilter: function() {
        if(!this._unmarkAll) {
            this._unmarkAll = Ext._create('Ext.menu.Item', {
                text: 'Desmarcar todos',
                scope: this,
                hideOnClick: false,
                handler: function() {
                    this.getOpenFilter().setChecked(false);
                    this.getWaitingForCustomerServiceFilter().setChecked(false);
                    this.getInServiceFilter().setChecked(false);
                    this.getAwaitingRatingFilter().setChecked(false);
                    this.getTransferredFilter().setChecked(false);
                    this.getOutsourcedFilter().setChecked(false);
                    this.getWarrantyFilter().setChecked(false);
                    this.getTravelFilter().setChecked(false);
                    this.getCompletedFilter().setChecked(false);
                    this.getWaitingForDeliveryFilter().setChecked(false);
                    this.getUnderMaintenanceFilter().setChecked(false);
                    this.getNotRatedFilter().setChecked(false);

                    this.filterStatus = [];
                    this.removeFilterProperty('status_atual__status__in', 1000, false);
                    this.setFilterProperty('status_atual__status__in', this.filterStatus, 1000, true);
                    this.setCookie();
                }
            });
        }

        return this._unmarkAll;
    },

    getFilterMenu: function(cfg) {
        if(cfg.manager == 'solicitante') {
            if (!this._filterMenu) {
                this._filterMenu = [
                    {
                        text: 'Por Lotação de Origem',
                        scope:this,
                        handler:this.filterLotacao
                    },
                    {
                        text: 'Aguardando Avaliação',
                        group: 'status_atual',
                        checked: false,
                        scope: this,
                        handler: function() { this.changeFilter(this.aguardando_avaliacao); }
                    },
                    {
                        text: 'Concluído',
                        group: 'status_atual',
                        checked: false,
                        scope: this,
                        handler: function() { this.changeFilter(this.concluido); }
                    },
                    {
                        text: 'Todos',
                        group: 'status_atual',
                        checked: false,
                        scope: this,
                        handler: function() { this.changeFilter(undefined); }
                    },
                    {
                        text: 'Exceto Concluído',
                        group: 'status_atual',
                        checked: true,
                        scope: this,
                        handler: function() { this.changeFilter(this.concluido, true); }
                    },
                ];
            }
            return this._filterMenu;
        }

        if(cfg.manager == 'atendente') {
            if (!this._filterMenu) {
                this._filterMenu = [
                    {
                        text: 'Concluído',
                        group: 'status_atual',
                        checked: false,
                        scope: this,
                        handler: function() {
                            this.addFilterProperty('cancelado', true, -1); //exclude Cancelado = true
                            this.changeFilter(this.concluido);

                        }
                    },
                    {
                        text: 'Todos',
                        group: 'status_atual',
                        checked: false,
                        scope: this,
                        handler: function() {
                            this.setSortProperty('urgente','DESC', false);
                            this.setSortProperty('data_fila_atendimento', 'ASC', false);
                            this.removeFilterProperty('cancelado', undefined, false);
                            this.changeFilter(undefined);
                        }
                    },
                    {
                        text: 'Exceto Concluído',
                        group: 'status_atual',
                        checked: false,
                        scope: this,
                        handler: function() {
                            this.setSortProperty('urgente','DESC', false);
                            this.setSortProperty('data_fila_atendimento', 'ASC', false);
                            this.removeFilterProperty('cancelado', undefined, false);
                            this.changeFilter(this.concluido, true);
                            this.addFilterProperty('cancelado', true, -1); //exclude Cancelado = true
                        }
                    },
                    {
                        text: 'Exceto Avaliação',
                        group: 'status_atual',
                        checked: true,
                        scope: this,
                        handler: function() {
                            this.setSortProperty('urgente','DESC', false);
                            this.setSortProperty('data_fila_atendimento', 'ASC', false);
                            this.removeFilterProperty('status_atual__status', undefined, false);
                            this.setFilterProperty('status_atual__status', this.concluido, -1, false); //exclude Concluido
                            this.addFilterProperty('status_atual__status', 4, -1); //exclude Aguardando Avaliacao status==4
                            this.addFilterProperty('cancelado', true, -1); //exclude Cancelado = true
                        }
                    }
                ];
            }
            return this._filterMenu;
        }

        if(cfg.manager == 'gerente' || cfg.manager == 'adm') {
            if (!this._filterMenu) {
                this._filterMenu = [
                        {
                            text: 'Por Lotação de Origem',
                            scope:this,
                            handler:this.filterAllLocations
                        },
                        {
                            text: 'Por Serviço',
                            scope:this,
                            handler:this.filterService
                        },
                        {
                        text: 'Status',
                        menu: [
                            this.getOpenFilter(),
                            this.getWaitingForCustomerServiceFilter(),
                            this.getInServiceFilter(),
                            this.getAwaitingRatingFilter(),
                            this.getTransferredFilter(),
                            this.getOutsourcedFilter(),
                            this.getWarrantyFilter(),
                            this.getTravelFilter(),
                            this.getCompletedFilter(),
                            this.getWaitingForDeliveryFilter(),
                            this.getUnderMaintenanceFilter(),
                            this.getNotRatedFilter(),
                            '-',
                            this.getMarkAllFilter(),
                            this.getUnmarkAllFilter()
                        ]
                    },
                ];
            }
            return this._filterMenu;
        }

        return false;
    },

    filterArea: function(param) {
        if (param==1) {
            this.removeFilterProperty('servico__in', [], false);
            this.setFilterProperty('servico__in', [6], 101);
        }
        else if (param==2) {
            this.removeFilterProperty('servico__in', [], false);
            this.setFilterProperty('servico__in', [5], 101);
        }
        else if(param==3) {
            this.removeFilterProperty('servico__in', [], false);
            this.setFilterProperty('servico__in', [4], 101);
        }
        else if (param==4) {
            var values = [2, 4, 3, 6, 5, 4];
            this.removeFilterProperty('servico__in', [], false);
            this.setFilterProperty('servico__in', values, 101);
        }
    },

    getEditarButton: function() {
        if(!this._editarButton)
            this._editarButton = Ext._create('Ext.Button', {
                text: 'Editar',
                iconCls: 'icon-core icon-core-edit',
                scope: this,
                handler: this.updateItem
            });

        return this._editarButton;
    },

    reportProtocolRenderer: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var wnd = window.open(
                '/athenas/SiatuChamado/renderer_document_to_print/?movement=' + selected.get('pk'),
                '_to_printer',
                (new SquareScreen(0.85)).toString() + ', scrollbars=yes'
            );
        }
        else
            Ext.Msg.show({
                title: 'Relatório de chamado',
                msg: 'Primeiro selecione o chamado que deseja gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: [
                    this.getEditarButton(),
                    '-',
                    'Buscar por :',
                    ' ',
                    this.getKeywordField(),
                    '-',
                ]
            });
            if(cfg.manager == 'gerente' || cfg.manager == 'adm' || cfg.manager=='atendente' ) {
                this._toolbar.add(
                    [
                        {
                            text: 'Status',
                            iconCls: 'icon-siatu icon-siatu-atendimento',
                            menu:[
                                {
                                    text: 'Atender',
                                    scope: this,
                                    handler: this.atender_chamado,
                                    iconCls: 'icon-siatu icon-siatu-atendimento'
                                },
                                {
                                    text: 'Concluir',
                                    scope: this,
                                    iconCls: 'icon-siatu icon-siatu-concluido',
                                    handler: function() {
                                                    // jrma
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected.get('atendentes').length > 0 || selected.get('terceiro_interno').length > 0)
                                                    {
                                                        this.concluir_chamado();
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Concluir',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK,
                                                            msg: 'Você deve adicionar um atendente ou um terceirizado para concluir.'
                                                        });
                                                    }
                                                }
                                },
                                {
                                    text: 'Aguardando entrega',
                                    scope: this,
                                    handler: this.status_aguarda_entrega,
                                    iconCls: 'icon-siatu icon-siatu-entrega'
                                },
                                {
                                    text: 'Em manutenção',
                                    scope: this,
                                    handler: this.status_manutencao,
                                    iconCls: 'icon-siatu icon-siatu-manutencao'
                                },
                                {
                                    text: 'Terceirizada',
                                    scope: this,
                                    handler: function() {
                                        this.change_others_state({status: 6, status_display: 'Terceirizada'});
                                    },
                                    iconCls: 'icon-siatu icon-siatu-terceirizada'
                                },
                                {
                                    text: 'Garantia',
                                    scope: this,
                                    handler: function() {
                                        this.change_others_state({status: 7, status_display: 'Garantia'});
                                    },
                                    iconCls: 'icon-siatu icon-siatu-garantia'
                                },
                                {
                                    text: 'Em Viagem',
                                    scope: this,
                                    handler: function() {
                                        this.change_others_state({status: 8, status_display: 'Em Viagem'});
                                    },
                                    iconCls: 'icon-siatu icon-siatu-viagem'
                                },
                                {
                                    text: 'Neutralizar Avaliação de Chamado',
                                    scope: this,
                                    handler: this.neutralizar_chamado,
                                    iconCls: 'icon-siatu icon-siatu-automatico'
                                },

                            ]

                        }
                    ]
                );
            }

            if(cfg.manager=='solicitante') {
                this._toolbar.remove(this.getEditarButton());
                this._toolbar.insert(0,
                    {
                        text: 'Novo',
                        iconCls: 'icon-core icon-core-add',
                        scope: this,
                        handler: this.verifica
                    }
                );
                this._toolbar.add([
                    this.getAvaliarButton(),
                    this.getCancelarButton()
                ]);
            }

            if(cfg.manager=='atendente') {
                this._toolbar.insert(0,
                    {
                        text: 'Novo',
                        iconCls: 'icon-core icon-core-add',
                        scope: this,
                        handler: this.solicitacaoGerente
                    }
                );
                this._toolbar.add([
                    {
                        text: 'Ações',
                        iconCls: 'icon-siatu icon-siatu-manutencao',
                        scope: this,
                        menu: [
                            this.getPedirChamadoButton(),
                            this.getReplicaButton(),
                            {
                                text: 'Pedidos transferência',
                                iconCls: 'icon-siatu icon-siatu-pedidos-transferencia',
                                scope: this,
                                handler: this.manager_transferencia

                            },
                            this.getReincidenciaAtendenteButton(),

                        ]
                    },
                ]);
            }

            if(cfg.manager=='gerente') {
                this._toolbar.insert(0,
                    {
                        text: 'Novo',
                        iconCls: 'icon-core icon-core-add',
                        scope: this,
                        handler: this.solicitacaoGerente
                    }
                );
                this._toolbar.add([
                    this.getReincidenciaGerenteButton(),
                    {
                        text: 'Urgencia',
                        iconCls: 'icon-siatu icon-siatu-urgente',
                        scope: this,
                        menu:[
                            {
                                text: 'Urgente',
                                iconCls: 'icon-siatu icon-siatu-urgente',
                                scope: this,
                                handler: this.urgente
                            },
                            {
                                text: 'Não Urgente',
                                iconCls: 'icon-siatu icon-siatu-urgente',
                                scope: this,
                                handler: this.nao_urgente
                            },
                        ]

                    },
                    // {
                    //     text: 'Urgente',
                    //     iconCls: 'icon-siatu icon-siatu-urgente',
                    //     scope: this,
                    //     handler: this.urgente
                    // },
                    // {
                    //     text: 'Não Urgente',
                    //     iconCls: 'icon-siatu icon-siatu-urgente',
                    //     scope: this,
                    //     handler: this.nao_urgente
                    // },
                    this.getCancelarButton(),
                    this.getDistribuicaoGerenteButton(),

                    ]);
            }

            var filterMenu = this.getFilterMenu(cfg);
            if(filterMenu)
                this._toolbar.add([
                    // '->',
                    '-',
                    {
                        text: 'Filtro',
                        iconCls: 'icon-patrimonio icon-pat-filter',
                        menu: filterMenu
                    }
                ]);
        }
        return this._toolbar;
    },

    getDistribuicaoGerenteButton: function() {
        if(!this._distribuicaoGerenteButton)
            this._distribuicaoGerenteButton = Ext._create('Ext.Button', {
                text: 'Distribuição Múltipla',
                iconCls: 'icon-siatu icon-siatu-transferido-atendente',
                scope: this,
                handler: this.distribuicao_gerente
            });

        return this._distribuicaoGerenteButton;
    },

    distribuicao_gerente: function() {

        var selected = this.getSelectionModel().getSelections();

        if(selected.length >= 2) {
            chamado_atendentes = false;
            chamado_servico = false;
            chamado_status = false;
            servico_cmp = selected[0].data.servico;
            for (var i=0; i<selected.length; i++) {
                if(selected[i].data.atendentes.length>0)
                {
                    chamado_atendentes = true;
                    break;
                }
                if(selected[i].data.servico != servico_cmp) {
                    chamado_servico = true;
                    break;
                }
                if( (selected[i].data.status_atual != "Aberto") && (selected[i].data.status_atual != "Aguardando atendimento") ) {
                    chamado_status = true;
                    break;
                }
            }
            if(chamado_atendentes) {
                Ext.Msg.show({
                    title: 'Distribuição Múltipla',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Você deve selecionar chamados sem atendentes atribuidos.'
                });
            } else if(chamado_servico) {
                Ext.Msg.show({
                    title: 'Distribuição Múltipla',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Você deve selecionar chamados do mesmo serviço.'
                });
            } else if(chamado_status) {
                Ext.Msg.show({
                    title: 'Distribuição Múltipla',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Você deve selecionar chamados com status Aberto ou Aguardando atendimento.'
                });
            } else {
                Ext._create('common.siatu.chamado.WindowDistribuir',{
                    action: 'update',
                    width: 500,
                    title: 'Distribuição Múltipla',
                    params: {chamados: selected},
                    listeners: {
                        scope: this,
                        close: function () {
                            this.getStore().reload();
                        }
                    }
                }).show();
            }
        } else {
            Ext.Msg.show({
                title: 'Distribuição Múltipla',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Você deve selecionar dois ou mais chamados.'
            });
        }
    },

    getAvaliarButton: function() {
        if(!this._avaliarButton)
            this._avaliarButton = Ext._create('Ext.Button', {
                text: 'Avaliar',
                iconCls: 'icon-siatu icon-siatu-avaliar',
                scope: this,
                handler: this.avaliar
            });

        return this._avaliarButton;
    },

    getReplicaButton: function() {
        if(!this._replicaButton)
            this._replicaButton = Ext._create('Ext.Button', {
                text: 'Replicar avaliação',
                iconCls: 'icon-siatu icon-siatu-avaliar',
                scope: this,
                handler: this.replicar
            });

        return this._replicaButton;
    },

    getCancelarButton: function() {
        if(!this._cancelarButton)
            this._cancelarButton = Ext._create('Ext.Button', {
                text: 'Cancelar',
                iconCls: 'icon-siatu icon-siatu-cancelado',
                scope: this,
                handler: this.cancelar
            });

        return this._cancelarButton;
    },

    getPedirChamadoButton: function() {
        if(!this._pedirChamadoButton)
            this._pedirChamadoButton = Ext._create('Ext.Button', {
                text: 'Pedir chamado',
                iconCls: 'icon-core icon-core-add',
                scope: this,
                handler: this.pedir_chamado
            });

        return this._pedirChamadoButton;
    },

    getReincidenciaAtendenteButton: function() {
        if(!this._reincidenciaAtendenteButton)
            this._reincidenciaAtendenteButton = Ext._create('Ext.Button', {
                text: 'Reincidência',
                iconCls: 'icon-siatu icon-siatu-reincidencia',
                scope: this,
                handler: this.reincidencia_atendente
            });

        return this._reincidenciaAtendenteButton;
    },

    getReincidenciaGerenteButton: function() {
        if(!this._reincidenciaGerenteButton)
            this._reincidenciaGerenteButton = Ext._create('Ext.Button', {
                text: 'Reincidência',
                iconCls: 'icon-siatu icon-siatu-reincidencia',
                scope: this,
                handler: this.reincidencia_gerente
            });

        return this._reincidenciaGerenteButton;
    },

    getActionColumn: function() {
        if(!this._actionColumn)
            this._actionColumn = Ext._create('Ext.grid.ActionColumn', {
                width: 65,
                scope: this,
                items: [
                    {
                        iconCls: 'icon-16px icon-core icon-core-edit',
                        tooltip: 'Editar item.',
                        handler: function(action, index) {
                            var record = this.getStore().getAt(index);
                            record && this.updateItem(record);
                        }
                    },
                ]
            });

        return this._actionColumn;
    },

    manager_transferencia: function() {
        Ext._create('common.siatu.chamado.ManagerTransfExterna',{
        }).show();
    },

    solicitacaoGerente: function(values) {
        values = core.nullValue(values, {});

        Ext._create('common.siatu.solicitacao.WindowGerente',{
            action: 'create',
            params: {
                concluido: this.concluido
            },
            values: values,
            callback: {
                success: {
                    scope: this,
                    fn: function() {
                        this.changeFilter(this.concluido, true);
                    }
                }
            }
        }).show();
    },

    verifica: function() {
        if (this.qtde_chamados_avaliar > 0) {
            Ext.Msg.show({
                title: 'Funcionalidade temporariamente indisponível',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Favor avaliar os chamados pendentes antes de prosseguir.'
            });
            this.changeFilter(this.aguardando_avaliacao);
        }
        else {
            this.solicitacao();
        }
    },

    solicitacao: function(values) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Buscando informações do usuário...'});

        values = core.nullValue(values, {});

        mask.show();
        rest.doRequest(
            rest.getRoute('telefone_usuario', false, 'GET', {
                scope: this,
                callback: function(opts, success, request) {
                    mask.hide();
                    mask = null;

                    if(success) {
                        var rst = Ext.decode(request.responseText);

                        if(rst.success)
                            Ext.applyIf(values, rst.values);

                    }

                    Ext._create('common.siatu.solicitacao.WindowSolicitante',{
                        action: 'create',
                        params: {solicitante: this.solicitante, concluido: this.concluido},
                        values: values,
                        callback: {
                            success: {
                                scope: this,
                                fn: function() {
                                    this.changeFilter(this.concluido, true);
                                }
                            }
                        }
                    }).show();
                }
            })
        );
    },

    avaliar: function() {

        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            if(selected.get('avaliacao')!='' || selected.get('status_atual')!='Aguardando avaliação') {
                console.debug("Item bloqueado para avaliação.");
                return;
            }
            Ext._create('common.siatu.chamado.avaliacao.Window',{
                action: 'create',
                title: 'Avaliação',
                relatorio_display: selected.get('relatorio_display'),
                params: {chamado: selected.get('pk')},
                callback: this.avaliacao_callback
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Avaliação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para avaliar.'
            });
    },

    replicar: function() {

        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            Ext._create('common.siatu.chamado.avaliacao.WindowReplica',{
                action: 'update',
                title: 'Replicar avaliação',
                oId: selected.get('avaliacao_pk'),
                values: selected.data,
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                            this.getReplicaButton().disable();
                        }
                    }
                }
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Replicar avaliação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para replicar.'
            });
    },

    cancelar: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            Ext._create('common.siatu.chamado.WindowCancelar',{
                action: 'update',
                title: 'Cancelar',
                oId: selected.get('pk'),
                params: {cancelado: true},
                callback: this.cancelar_callback
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Cancelar',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para cancelar.'
            });
    },

    reincidencia_atendente: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('common.siatu.chamado.reincidencia.WindowAtendente',{
                action: 'update',
                title: 'Reincidência',
                oId: selected.get('reincidencia'),
                values: 'remote',
                confirm_atendente: selected.get('reincidencia_confirm_atendente'),
                params: {atendente: true},
                chamado_anterior: selected.get('chamado_anterior_pk'),
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
        else
            Ext.Msg.show({
                title: 'Reincidência',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para conferir.'
            });
    },

    reincidencia_gerente: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('common.siatu.chamado.reincidencia.WindowGerente',{
                action: 'update',
                title: 'Reincidência',
                oId: selected.get('reincidencia'),
                values: 'remote',
                parecer: selected.get('reincidencia_parecer'),
                confirm_atendente: selected.get('reincidencia_confirm_atendente'),
                params: {gerente: true},
                chamado_anterior: selected.get('chamado_anterior_pk'),
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
        else
            Ext.Msg.show({
                title: 'Reincidência',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para conferir.'
            });
    },

    urgente: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('common.siatu.chamado.urgente.Window',{
                action: 'update',
                title: 'Urgente',
                oId: selected.get('pk'),
                values: 'remote',
                params: {urgente: true},
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
        else
            Ext.Msg.show({
                title: 'Urgente',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });
    },

    nao_urgente: function() {
        var selection = this.getSelectionModel().getSelections();
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});

        if(selection.length > 0) {
            mask.show();

            rest.doRequest(
                rest.getRoute('nao_urgente', false, 'POST', {
                    scope: this,
                    params: {
                        pks: selection.map(function(item) { return item.get('pk'); })
                    },
                    callback: function() {
                        mask.hide();
                        mask = undefined;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success) {
                            this.getStore().reload();
                            Ext.Msg.show({
                                title: 'Atenção',
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                        }
                        else
                            Ext.Msg.show({
                                title: 'Atenção',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    },
                    failure: function(xhr) {
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponível no momento.'
                        });
                    },
                })
            );
        }
        else
            Ext.Msg.show({
                title: 'Urgente',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });
    },

// updateItem sobrescrita:
// adicionando disableSave para apenas visualizar informações
// alterando callback para remover selecao row
    updateItem: function(record) {
        if(!this.allowUpdate)
            return;

        if(record instanceof Ext.Button)
            record = undefined;

        var selected = core.nullValue(record, this.getSelectionModel().getSelected());

        if(selected) {
            this.factoryRestfulWindow({
                action: 'update',
                oId: selected.get('pk'),
                values: selected.data,
                // params: this.getParams(),
                params: Ext.applyIf({nao_institucional: 'false'}, this.getParams()),
                disableSave: this.disableSave,
                callback: this.update_callback,
            }).show();
        }
        else
            if(this.disableSave)
                Ext.Msg.show({
                    title: 'Informações',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Primeiro selecione um item para obter informações.'
                });
            else
                Ext.Msg.show({
                    title: 'Editando',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Primeiro selecione um item para editar.'
                });
    },

    pedir_chamado: function() {
        this.getPedirChamadoButton().disable();
        var rest = Ext._create('common.siatu.atendente.Restful', {});
        conf = {
            scope: this,
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if(rst.success) {
                    this.getStore().load();
                }
                else {
                    Ext.Msg.show({
                        title: 'Pedir chamado',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: rst.message
                    });
                }
                this.getPedirChamadoButton().enable();
            },
            failure: function(request) {
                console.debug('Falha na requisição');
                this.getPedirChamadoButton().enable();
            },
        };
        rest.doRequest(rest.getRoute('action_pedir_chamado', null, null, conf));
    },

    atender_chamado:function() {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            var rest = Ext._create('common.siatu.chamado.status.Restful', {});
            var cfg = {
                externalCallback: this.status_callback,
                params: {
                    status: 3,
                    chamado: selected.get('pk'),
                    insert: true,
                } //status 3 == Em atendimento
            };
            rest.create(
                cfg,
                {
                    el: this.getEl(),
                    waitMessage: 'Persistindo os dados.'
                }
            );
        }
        else {
            Ext.Msg.show({
                title: 'Status',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Favor selecionar um chamado.'
            });
        }
    },

    neutralizar_chamado:function() {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {

            var wnd = Ext._create('common.siatu.chamado.avaliacao.NeutralizarWindow', {
                modal: true,
                params: {
                    pk: selected.data.pk,
                },
            });
            wnd.show();
        }
        else {
            Ext.Msg.show({
                title: 'Status',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Favor selecionar um chamado.'
            });
        }
    },

    status_aguarda_entrega: function() {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            var rest = Ext._create('common.siatu.chamado.status.Restful', {});
            var cfg = {
                externalCallback: this.status_callback,
                params: {
                    status: 10,
                    chamado: selected.get('pk'),
                    insert: true,
                } //status 10 == Aguardando Entrega
            };
            rest.create(
                cfg,
                {
                    el: this.getEl(),
                    waitMessage: 'Persistindo os dados.'
                }
            );
        }
        else {
            Ext.Msg.show({
                title: 'Status',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Favor selecionar um chamado.'
            });
        }
    },

    status_manutencao: function() {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            var rest = Ext._create('common.siatu.chamado.status.Restful', {});
            var cfg = {
                externalCallback: this.status_callback,
                params: {
                    status: 11,
                    chamado: selected.get('pk'),
                    insert: true,
                } //status 11 == Em Manutenção
            };
            rest.create(
                cfg,
                {
                    el: this.getEl(),
                    waitMessage: 'Persistindo os dados.'
                }
            );
        }
        else {
            Ext.Msg.show({
                title: 'Status',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Favor selecionar um chamado.'
            });
        }
    },

    change_others_state: function(values) {
      var selected = this.getSelectionModel().getSelected();
      values = core.nullValue(values, {});
        if(selected) {
            Ext._create('common.siatu.chamado.status.Window',{
                action: 'create',
                values: values,
                params: {chamado: selected.get('pk')},
                callback: this.status_callback,
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Status',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });
    },

    concluir_chamado: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('common.siatu.chamado.status.concluirWindow', {
                action: 'update',
                title: 'Concluir Chamado',
                oId: selected.get('pk'),
                values: selected.data,
                params: Ext.applyIf({nao_institucional: 'false'}, this.getParams()),
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                },
                status_callback: this.status_callback,
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Status',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        if (cfg.filterStatus)
            this.filterStatus = cfg.filterStatus;
        else {
            this.filterStatus = [1, 2, 3, 5, 6, 7, 8, 10, 11, 12];

        this.serviceSelect = [2, 4, 3, 6, 5, 4];

            // this.addFilterProperty('cancelado', true, -1); //exclude Cancelado = true
            // this.addFilterProperty('status_atual__status', 1, -1, false);
            // this.addFilterProperty('status_atual__status', 4, -1, false);
            // this.addFilterProperty('status_atual__status', 5, -1, false);
            // this.addFilterProperty('status_atual__status', 8, -1, false);
            // this.addFilterProperty('status_atual__status', 12, -1, false);
        }

        if (cfg.filterServico)
            this.filterServico = cfg.filterServico;
        else {
            this.filterServico = [];
        }

        Ext.applyIf(
            cfg,
            {
                update_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            }
        );

        Ext.apply(
            cfg,
            {
                allowRemove: false,
                columnAction: false
            }
        );
        common.siatu.chamado.Grid.superclass.constructor.call(this, cfg);

        if(!this.disableSave)
            this.getSelectionModel().on({
                scope: this,
                rowselect: function(grid, index, record) {
                    if( (record.get('status_atual')=='Concluído') || (record.get('status_atual')=='Aguardando avaliação') ) {
                        this.disableSave = true;
                    }
                    else {
                        this.disableSave = false;
                    }
                }
            });
    }
});
