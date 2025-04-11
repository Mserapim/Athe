Ext._define('raf.functionalactivityreport.GroupGrid', {
    extend: 'Ext.grid.GridPanel',

    factoryStore: function(cfg) {
        if(!this._groupStore) {
            this._groupStore = Ext._create('Ext.data.GroupingStore', {
                autoLoad: true,
                baseParams: {
                    employee: 0
                },
                proxy: Ext._create('Ext.data.HttpProxy', {
                    url: core.callAction('RAFFunctionalActivityReport', 'all_rafs'),
                }),
                groupField: 'year',
                groupDir: 'DESC',
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        {type: "integer", name: "pk"},
                        {type: "string", name: "month_unicode"},
                        {type: "integer", name: "month"},
                        {type: "integer", name: "year"},
                        {type: "integer", name: "employee_matricula"},
                        {type: "integer", name: "employee"},
                        {name: "icons"},
                    ]
                })
            });
        }

        return this._groupStore;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    {header: '', dataIndex: 'icons', width: 10, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Ano', dataIndex: 'year', width: 40},
                    {header: 'Mês', dataIndex: 'month_unicode', width: 80},
                ],
            });

        return this._columnModel;
    },


    setLocationsFollow: function(value, reload) {
        reload = (reload === undefined ? true : reload);

        this.locationsFollow(value);

        this.getStore().setBaseParam('locations_follow', this.locationsFollow());
        if(reload) {
            this.getStore().reload();
        }
    },

    locationsFollow: function(value) {

        if(value !== undefined)
            this._locationsFollow = value;

        return this._locationsFollow;
    },

    setValueEmployee: function(value) {

        this.employee(value);

        this.getStore().setBaseParam('employee', this.employee());
        this.getStore().reload();

    },

    employee: function(value) {

        if(value !== undefined)
            this._employee = value;

        return this._employee;
    },

    reopenRequest: function(selected) {
        Ext.Ajax.request({
            scope: this,
            url: core.callAction('RAFSolicitation', 'register_reopening'),
            callback: function() {
                core.invokeCallback((this.callback || {}).success);
                this.getStore().reload();
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);

                Ext.Msg.show({
                    title: 'Solicitar Reabertura do RAF',
                    msg: rst.message,
                    icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            failure: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Solicitar Reabertura do RAF',
                    msg: rst.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            params: {
                raf: selected.get('pk')
            },
        });
    },

    reopenRaf: function() {
        var selected = this.getSelectionModel().getSelected();
                
        if(selected) {
            
            Ext.Msg.show({
                title: 'Solicitar Reabertura do RAF',
                msg: 'Tem certeza que deseja solicitar a reabertura do RAF selecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    
                    this.reopenRequest(selected);
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Solicitar Reabertura do RAF',
                msg: 'Primeiro selecione o RAF',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    submitRaf: function() {
        var selected = this.getSelectionModel().getSelected();
        var rest = Ext._create('raf.functionalactivityreport.Restful');

        if(selected) {

            Ext.Msg.show({
                title: 'Submeter RAF',
                msg: 'Tem certeza que deseja submter o RAF selecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;

                    rest.submitRaf(
                        selected.get('pk'),
                        {
                            scope: this,
                            fn: function(rst) {
                                core.invokeCallback((this.callback || {}).success);
                                this.getStore().reload();

                                Ext.Msg.show({
                                    title: 'Submeter Raf',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function(message) {
                                Ext.Msg.show({
                                    title: 'Submeter Raf',
                                    msg: message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function() {}
                        }
                    );
                }
            });

        } else {
            Ext.Msg.show({
                title: 'Submeter Raf',
                msg: 'Primeiro selecione o RAF que deseja submeter',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }

    },

    openFollowAdjustmentWindow: function() {

        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            Ext._create('raf.functionalactivityreport.FollowAdjustmentWindow', {
                params: {
                    raf: selected.get('pk')
                },
                values: {
                    workerlocation_unicode: 'teste 1',
                    quiz_unicode: 'teste 2',
                    item_unicode: 'teste 3',
                    subitem_unicode: 'teste 4',
                },
                success: {
                    scope: this,
                    fn: function() {
                        this.getStore().reload();
                    }
                }
            }).show();

        } else {
            Ext.Msg.show({
                title: 'Acompanhar Solicitações',
                msg: 'Primeiro selecione o RAF que deseja acompanhar as solicitações.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }

    },

    getSubmitAction: function() {
        if(!this._submitAction){
            this._submitAction = new Ext.Button({
                xtype: 'button',
                text: 'Submeter RAF',
                iconCls: 'icon-core icon-core-document-arrow',
                scope: this,
                handler: function() {
                    this.submitRaf();
                }
            });
        }
        return this._submitAction;
    },

    getReopenAction: function() {
        if(!this._reopenAction){
            this._reopenAction = new Ext.Button({
                xtype: 'button',
                text: 'Solicitar Reabertura',
                iconCls: 'icon-raf icon-raf-open',
                scope: this,
                handler: function() {
                    this.reopenRaf();
                }
            });
        }
        return this._reopenAction;
    },

    getFollowAction: function() {
        if(!this._followAction){
            this._followAction = new Ext.Button({
                xtype: 'button',
                text: 'Acompanhamento',
                iconCls: 'icon-raf icon-raf-eye',
                scope: this,
                handler: function() {
                    this.openFollowAdjustmentWindow();
                }
            });
        }
        return this._followAction;
    },

    getManagentRaf: function() {
        Ext._create('raf.management.ManagementRAF', {
                values: { }
            }).show();
    },

    getExtractReport: function() {
        var employee = this.employee();
        var selected = this.getSelectionModel().getSelected();

        if(employee) {
          if (selected) {
              engine.mq.Report.request({
                  report: '/to/mpe/raf/espelho_raf',
                  waitMessage: 'Gerando os documentos...',
                  params: {
                      outfile: 'extrato-raf',
                      report_name: 'RAF',
                      raf: selected.get('pk'),
                  }
              });
          } else {
              Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Selecione um mês de referência para geração do RAF.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
                });
          }
        }
        else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getProcessingExtractReport: function() {
        var employee = this.employee();
        var selected = this.getSelectionModel().getSelected();

        if(employee) {
            if (selected) {
                engine.mq.Report.request({
                    report: '/to/mpe/raf/raf_eproc_processamento',
                    waitMessage: 'Gerando os documentos...',
                    params: {
                        outfile: 'extrato-processamento-eproc-'+selected.get('month')+'/'+selected.get('year')+'-'+selected.get('employee_matricula'),
                        report_name: 'Extrato de Processamento EProc - '+selected.get('employee_matricula')+' - '+selected.get('month')+'/'+selected.get('year'),
                        month: selected.get('month'),
                        year: selected.get('year'),
                        membro: selected.get('employee_matricula'),
                    }
                });
            } else {
                Ext.Msg.show({
                  title: 'Relatórios',
                  msg: 'Selecione um mês de referência para geração do Extrato de Processamento do EProc.',
                  icon: Ext.Msg.ERROR,
                  buttons: Ext.Msg.OK
                });
            }
        } else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getProcessosSemPromotoriaReport: function() {
        var employee = this.employee();
        var selected = this.getSelectionModel().getSelected();

        if(employee) {
            if (selected) {
                engine.mq.Report.request({
                    report: '/to/mpe/raf/raf_eproc_sem_promotoria',
                    waitMessage: 'Gerando os documentos...',
                    params: {
                        outfile: 'eproc-processos-sem-promotoria-'+selected.get('month')+'/'+selected.get('year')+'-'+selected.get('employee_matricula'),
                        report_name: 'EPROC - Processos sem Promotoria - '+selected.get('employee_matricula')+' - '+selected.get('month')+'/'+selected.get('year'),
                        month: selected.get('month'),
                        year: selected.get('year'),
                        membro: selected.get('employee_matricula'),
                    }
                });
            } else {
                Ext.Msg.show({
                  title: 'Relatórios',
                  msg: 'Selecione um mês de referência para geração da Relação de Processos sem Promotoria.',
                  icon: Ext.Msg.ERROR,
                  buttons: Ext.Msg.OK
                });
            }
        } else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getEExtImport: function() {
        var employee = this.employee();
        var selected = this.getSelectionModel().getSelected();

        if(employee) {
          if (selected) {
              engine.mq.Report.request({
                  report: '/to/mpe/raf/raf_eext_import',
                  waitMessage: 'Gerando os documentos...',
                  params: {
                      outfile: 'eext-importacao',
                      report_name: 'RAF',
                      raf: selected.get('pk'),
                  }
              });
          } else {
              Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Selecione um mês de referência para geração do RAF.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
                });
          }
        }
        else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getEprocIn: function() {
        var employee = this.employee();
        var selected = this.getSelectionModel().getSelected();

        if(employee) {
          if (selected) {
              engine.mq.Report.request({
                  report: '/to/mpe/raf/raf_eproc_entradas',
                  waitMessage: 'Gerando os documentos...',
                  params: {
                      outfile: 'eproc-entradas',
                      report_name: 'RAF',
                      raf: selected.get('pk'),
                  }
              });
          } else {
              Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Selecione um mês de referência para geração do RAF.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
                });
          }
        }
        else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getEprocOut: function() {
        var employee = this.employee();
        var selected = this.getSelectionModel().getSelected();

        if(employee) {
          if (selected) {
              engine.mq.Report.request({
                  report: '/to/mpe/raf/raf_eproc_saidas',
                  waitMessage: 'Gerando os documentos...',
                  params: {
                      outfile: 'eproc-saidas',
                      report_name: 'RAF',
                      raf: selected.get('pk'),
                  }
              });
          } else {
              Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Selecione um mês de referência para geração do RAF.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
                });
          }
        }
        else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    openProductivityReportPeriod: function() {
        Ext._create('raf.report.ProductivityReportPeriodWindow', {
            values: { }
        }).show();
    },

    getExtractAdjustment: function() {
        var employee = this.employee();
        var selected = this.getSelectionModel().getSelected();
        if(employee) {
            if (selected) {
                engine.mq.Report.request({
                    report: '/to/mpe/raf/extrato_solicitacoes',
                    waitMessage: 'Gerando os documentos...',
                    params: {
                        outfile: 'extrato-solicitacoes-eproc-'+selected.get('month')+'/'+selected.get('year')+'-'+selected.get('employee_matricula'),
                        report_name: 'Extrato de Solcitações - '+selected.get('employee_matricula')+' - '+selected.get('month')+'/'+selected.get('year'),
                        employee: selected.get('employee'),
                        initial_month: selected.get('month'),
                        initial_year: selected.get('year'),
                        final_month: selected.get('month'),
                        final_year: selected.get('year'),
                    }
                });
            } else {
                Ext.Msg.show({
                  title: 'Relatórios',
                  msg: 'Selecione um mês de referência para geração do Extrato de Solcitações.',
                  icon: Ext.Msg.ERROR,
                  buttons: Ext.Msg.OK
                });
            }
        } else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    openConsolidatedReportPeriod: function() {

        Ext._create('raf.report.ExtractReportLocationPeriodWindow', {
            values: {
                locationsFilter: this.locationsFollow()
            }
        }).show();
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = Ext._create('Ext.Toolbar', {
                items: [
                    {
                        text: 'Controle',
                        // iconCls: 'icon-raf icon-raf-report',
                        menu: [
                            // {
                            //     text: 'Gerenciamento',
                            //     iconCls: 'icon-raf icon-eye',
                            //     hidden: cfg.management_enable === 1 ? false : true,
                            //     scope: this,
                            //     handler: function() { this.getManagentRaf(); }
                            // },
                            // '-',
                            {
                                text: 'Pesquisar por número',
                                iconCls: 'icon-core icon-core-select',
                                scope: this,
                                handler: function() {
                                    Ext._create('raf.searchprocessnumber.SearchProcessNumberWindow', { }).show();
                                }
                            },
                            {
                                text: 'Acompanhamento das Solicitação de Ajustes',
                                iconCls: 'icon-raf icon-raf-eye',
                                scope: this,
                                handler: function() {
                                    this.openFollowAdjustmentWindow();
                                }
                            },
                            '-',
                            {
                                text: 'Relatórios',
                                iconCls: 'icon-raf icon-raf-report',
                                scope: this,
                                menu: [
                                    {
                                      text: 'Consolidado por Período/Lotação',
                                      iconCls: 'icon-raf icon-raf-report-pdf',
                                      scope: this,
                                      handler: function() { this.openConsolidatedReportPeriod(); }
                                    },
                                    {
                                        text: 'Espelho Mensal',
                                        iconCls: 'icon-raf icon-raf-report-pdf',
                                        scope: this,
                                        handler: function() { this.getExtractReport(); }
                                    },
                                    {
                                        text: 'Importação e-Proc',
                                        iconCls: 'icon-raf icon-raf-report-pdf',
                                        scope: this,
                                        menu: [
                                            {
                                                text: 'Relatório de Entradas',
                                                iconCls: 'icon-raf icon-raf-report-pdf',
                                                scope: this,
                                                handler: function() { this.getEprocIn(); }
                                            },
                                            {
                                                text: 'Relatório de Saídas',
                                                iconCls: 'icon-raf icon-raf-report-pdf',
                                                scope: this,
                                                handler: function() { this.getEprocOut(); }
                                            },
                                            '-',
                                            {
                                                text: 'Relação de Processos sem Promotoria',
                                                iconCls: 'icon-raf icon-raf-report-pdf',
                                                scope: this,
                                                handler: function() { this.getProcessosSemPromotoriaReport(); }
                                            },
                                            {
                                                text: 'Extrato de Processamento',
                                                iconCls: 'icon-raf icon-raf-report-pdf',
                                                scope: this,
                                                handler: function() { this.getProcessingExtractReport(); }
                                            },
                                        ]
                                    },
                                    {
                                        text: 'Importação e-Ext',
                                        iconCls: 'icon-raf icon-raf-report-pdf',
                                        scope: this,
                                        menu: [
                                            {
                                                text: 'Relatório de Importação',
                                                iconCls: 'icon-raf icon-raf-report-pdf',
                                                scope: this,
                                                handler: function() { this.getEExtImport(); }
                                            }
                                        ]
                                    },
                                    '-',
                                    {
                                        text: 'Extrato de Solicitações',
                                        iconCls: 'icon-raf icon-raf-report-pdf',
                                        scope: this,
                                        handler: function() { this.getExtractAdjustment(); }
                                    },
                                    // {
                                    //   text: 'Produtividade por Período/Membro/Lotação',
                                    //   iconCls: 'icon-raf icon-raf-report-pdf',
                                    //   scope: this,
                                    //   handler: function() { this.openProductivityReportPeriod(); }
                                    // },
                                ]
                            },
                        ]
                    },
                    '->',
                    this.getReopenAction(),
                    '-',
                    this.getSubmitAction()
                ]

            });
        }

        return this._toolbar;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                loadMask: true,
                tbar: this.getToolbar(cfg),
                ds: this.factoryStore(cfg),
                colModel: this.getColumnModel(),
                view: new Ext.grid.GroupingView({
                    startCollapsed: true,
                    forceFit: true,
                    showGroupName: false,
                    enableNoGroups: false,
                    enableGroupingMenu: false,
                    hideGroupedColumn: true
                })
            }
        );

        raf.functionalactivityreport.GroupGrid.superclass.constructor.call(this, cfg);
    }
});
