Ext._define('corregedoria.inspection.inspection.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'corregedoria.inspection.inspection.Restful',
    restWindow: 'corregedoria.inspection.inspection.Window',

    // configOrderToolBar: ['add', 'remove', 'search', 'filling', 'sign', 'communication', 'menu', 'response', 'applyFilter', 'menuRecommendation', 'viewReport', '-'],
    configOrderToolBar: ['search', 'filling', 'sign', 'communication', 'menu', 'response', 'applyFilter', 'menuRecommendation', 'viewReport', '-'],

    getInspectionReport: function() {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            var var_report = '';
            if (selected.data.inspection_type) {
                if (selected.data.inspection_type == 1) {
                    var_report = selected.get('execution_organ_instance') == 1 ? '/to/mpe/corregedoria/inspection/inspection_report' : '/to/mpe/corregedoria/inspection/inspection_report_procuratorate';
                }
                if (selected.data.inspection_type == 2) {
                    var_report = '/to/mpe/corregedoria/inspection/inspection_report_especialgroup';
                }
                if (selected.data.inspection_type == 3) {
                    var_report = '/to/mpe/corregedoria/inspection/inspection_report_auxiliarorgan';
                }
                engine.mq.Report.request({
                    report: var_report,
                    waitMessage: 'Gerando os relatório...',
                    params: {
                        outfile: 'relatorio-inspecao-'+selected.get('execution_organ_slugify'),
                        report_name: 'Relatório de Inspeção - '+selected.get('execution_organ_unicode'),
                        all: 1,
                        inspection: selected.get('pk'),
                    }
                });
            } else {
                Ext.Msg.show({
                    title: 'Preencher Inspeção/Correição',
                    msg: 'Inspeção sem definição de tipo.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        } else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione a inspeção/correição para geração do relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    reload_data: function(item) {
        item = (item === undefined ? 'all' : item);
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            var values = {inspection: selected.get('pk'), item: item};
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Atualizando dados da inspeção...'});
            Ext.Msg.show({
                title: 'Atualizar dados da Inspeção/Correição',
                msg: 'Tem certeza que deseja atualizar os dados da inspeção?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('INSPECTIONInspection', 'reloadData'),
                        callback: function() {
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Atualizar dados da Inspeção/Correição',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                                this.getStore().reload();
                            } else {
                                Ext.Msg.show({
                                    title: 'Atualizar dados da Inspeção/Correição',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Atualizar dados da Inspeção/Correição',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: values,
                    });
                }
            });
        }
        else {
            Ext.Msg.show({
                title: 'Atualizar dados da Inspeção/Correição',
                msg: 'Selecione uma Inspeção/Correição',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    finalize: function() {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            var values = {inspection: selected.get('pk'), };
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Atualizando dados da inspeção...'});
            Ext.Msg.show({
                title: 'Finalizar a Inspeção/Correição',
                msg: 'Tem certeza que deseja finalizar a inspeção?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('INSPECTIONInspection', 'finalize'),
                        callback: function() {
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Finalizar a Inspeção/Correição',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                                this.getStore().reload();
                            } else {
                                Ext.Msg.show({
                                    title: 'Finalizar a Inspeção/Correição',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Finalizar a Inspeção/Correição',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: values,
                    });
                }
            });
        }
    },

    getAnalyzeWindow: function() {
        Ext._create('corregedoria.inspection.inspection.analyze_recommendation.analyzeWindow', {
            values: { },
        }).show();
    },

    openHistoryInspectionReport: function() {
        Ext._create('corregedoria.inspection.report.HistoryInspectionReport', {
            values: { }
        }).show();
    },

    getMenuAction: function() {
        if(!this._downmenuAction){
            this._downmenuAction = new Ext.Button({
                xtype: 'button',
                text: 'Opções',
                iconCls: 'icon-crgmpe icon-crgmpe-settings',
                menu: [
                    {
                        text: 'Download',
                        iconCls: 'icon-crgmpe icon-crgmpe-floppy',
                        scope: this,
                        menu: [
                            {
                                text: 'Relatório da Inspeção/Correição (PDF)',
                                iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                                scope: this,
                                handler: function() { this.getInspectionReport(); }
                            },
                            '-',
                            {
                                text: 'Anexos da Inspeção/Correição (ZIP))',
                                iconCls: 'icon-crgmpe icon-crgmpe-application-x-gzip',
                                disabled: true,
                                scope: this,
                                handler: function() {  }
                            },
                        ]
                    }
                ]
            });
        }
        return this._downmenuAction;
    },

    getShowAll: function() {
        this.removeAllFilterPropertyLocal(true);
    },

    removeAllFilterPropertyLocal: function(reload) {
        var oldFilter = this.getFilter();

        oldFilter.forEach(
            function(item) {
                this.removeFilterProperty(item.property, item.stage, false);
            },
            this
        );

        if(reload)
            this.getStore().load();
    },

    getShowFinalized: function() {
        this.removeAllFilterPropertyLocal(false);

        this.addFilterProperty('finalized', true, 104, true);
    },

    getShowNoFinalized: function() {
        this.removeAllFilterPropertyLocal(false);

        this.addFilterProperty('finalized_at__isnull', true, 105, true);
    },

    getWaitingAnalyze: function() {
        this.removeAllFilterPropertyLocal(false);

        this.addFilterProperty('recommendations__deadlines__sent', true, 101, false);
        this.addFilterProperty('recommendations__deadlines__decision_at__isnull', true, 102, false);
        this.addFilterProperty('finalized_at__isnull', true, 105, true);
    },

    getDelayOfTime: function() {
        var now = new Date();
        var now_str = now.getFullYear() + '-' + (now.getMonth() + 1) + '-' + now.getDate();

        this.removeAllFilterPropertyLocal(false);
        this.addFilterProperty('finalized', false, 101, false);
        this.addFilterProperty('finalized_at__isnull', true, 102, false);
        this.addFilterProperty('recommendations__deadline__lt', now_str, 103, false);
        this.addFilterProperty('recommendations__finalized', false, 104, true);

    },

    getNotification: function() {
        this.removeAllFilterPropertyLocal(false);

        this.addFilterProperty('finalized_at__isnull', true, 105, false);
        this.addFilterProperty('notificationhistory__isnull', false, 107, true);
    },

    getNotificationDeadline: function() {
        now = new Date();

        this.removeAllFilterPropertyLocal(false);
        this.addFilterProperty('finalized_at__isnull', true, 105, false);
        this.addFilterProperty('notificationhistory__deadline__lt', now.getFullYear() + '-' + (now.getMonth() + 1) + '-' + now.getDate(), 106, false);
        this.addFilterProperty('notificationhistory__responded', false, 108, true);
    },

    getApplyFilterAction: function() {
        if(!this._applyFilterAction){
            this._applyFilterAction = new Ext.Button({
                xtype: 'button',
                text: 'Exibir',
                iconCls: 'icon-judicial icon-ejud-prepare-concurrence',
                menu: [
                    {
                        text: 'Aguardando Análise',
                        iconCls: 'icon-crgmpe icon-crgmpe-send-mail',
                        scope: this,
                        handler: function() { this.getWaitingAnalyze(); }
                    },
                    {
                        text: 'Atrasados',
                        iconCls: 'icon-crgmpe icon-crgmpe-clock-delay',
                        scope: this,
                        handler: function() { this.getDelayOfTime(); }
                    },
                    '-',
                    {
                        text: 'Notificações',
                        iconCls: 'icon-crgmpe icon-crgmpe-mail',
                        scope: this,
                        handler: function() { this.getNotification(); }
                    },
                    {
                        text: 'Notificações vencidas',
                        iconCls: 'icon-crgmpe icon-crgmpe-mail',
                        scope: this,
                        handler: function() { this.getNotificationDeadline(); }
                    },
                    '-',
                    {
                        text: 'Não Finalizados',
                        iconCls: 'icon-crgmpe icon-crgmpe-open',
                        scope: this,
                        handler: function() { this.getShowNoFinalized(); }
                    },
                    {
                        text: 'Finalizados',
                        iconCls: 'icon-crgmpe icon-crgmpe-read-only',
                        scope: this,
                        handler: function() { this.getShowFinalized(); }
                    },
                    '-',
                    {
                        text: 'Todos',
                        iconCls: 'icon-crgmpe icon-crgmpe-select',
                        scope: this,
                        handler: function() { this.getShowAll();  }
                    },
                ]
            });
        }
        return this._applyFilterAction;
    },

    getContent: function(inspection) {
        var rest = Ext._create('corregedoria.inspection.inspection.Restful');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'get_content'),
            scope: this,
            autoAbort: true,
            params: {
                inspection: inspection
            },
            callback: function() {
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;
                if(rst.success) {
                    return rst.content;
                    // this.getTilePanel().setPageContent(rst.content);
                }
                else
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Carregando informações',
                    msg: 'Recurso indisponivel no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    getMenuRecommendationAction: function() {
        if(!this._menuRecommendationAction){
            this._menuRecommendationAction = new Ext.Button({
                xtype: 'button',
                text: 'Opções',
                iconCls: 'icon-crgmpe icon-crgmpe-settings',
                menu: [
                    {
                        text: 'Notificações',
                        iconCls: 'icon-crgmpe icon-crgmpe-mail',
                        scope: this,
                        menu: [
                            {
                                text: 'Enviar notificação de atraso (via e-Doc)',
                                iconCls: 'icon-crgmpe icon-crgmpe-mail',
                                scope: this,
                                handler: function() {
                                    var selected = this.getSelectionModel().getSelected();
                                    var values = {};
                                    if (selected) {
                                        values = {
                                            inspection: selected.get('pk'),
                                            execution_organ: selected.get('execution_organ_unicode'),
                                            inspection_date_initial: selected.get('inspection_date_initial_formatted'),
                                            inspection_date_final: selected.get('inspection_date_final_formatted'),
                                        };
                                        Ext._create('corregedoria.inspection.inspection.follow_recommendation.NotifyPersonalized', {
                                            values: values,
                                        }).show();
                                    } else {
                                        Ext.Msg.show({
                                            title: 'Enviar notificação de atraso (via e-Doc)',
                                            msg: 'Primeiro selecione a Inspeção/Correição que deseja notificar.',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        });
                                    }
                                }
                            },
                            '-',
                            {
                                text: 'Histórico de notificações de atraso (via e-Doc)',
                                iconCls: 'icon-crgmpe icon-crgmpe-mail',
                                scope: this,
                                handler: function() {
                                    var selected = this.getSelectionModel().getSelected();
                                    var values = {};
                                    if (selected) {
                                        values = {
                                            inspection: selected.get('pk'),
                                            execution_organ: selected.get('execution_organ_unicode'),
                                            inspection_date_initial: selected.get('inspection_date_initial_formatted'),
                                            inspection_date_final: selected.get('inspection_date_final_formatted'),
                                        };
                                        Ext._create('corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Manage', {
                                            values: values,
                                        }).show();
                                    } else {
                                        Ext.Msg.show({
                                            title: 'Enviar notificação de atraso (via e-Doc)',
                                            msg: 'Primeiro selecione a Inspeção/Correição que deseja notificar.',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        });
                                    }
                                }
                            },
                        ]
                    },
                    '-',
                    {
                        text: 'Finalizar Inspeção/Correição',
                        iconCls: 'icon-crgmpe icon-crgmpe-read-only',
                        scope: this,
                        handler: function() { this.finalize();  }
                    },
                ]
            });
        }
        return this._menuRecommendationAction;
    },

    createInspection: function(inspection_type) {
        var_window = '';
        if (inspection_type) {
            if (inspection_type == 1){
                var_window = 'corregedoria.inspection.inspection.WindowExecutionOrgan';
            }
            else {
                if (inspection_type == 2){
                    var_window = 'corregedoria.inspection.inspection.WindowEspecialGroup';
                }
                else {
                    if (inspection_type == 3){
                        var_window = 'corregedoria.inspection.inspection.WindowAuxiliaryOrgan';
                    }
                }
            }
            Ext._create(var_window, {
                action: 'create',
                params: { inspection_type: inspection_type, gridInspection: this, }
            }).show();
        } else {
            console.log('sem difinição para o órgão inspecionado.');
        }
    },

    updateItem: function(values) {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if (selected.data.inspection_type) {
                if (selected.data.inspection_type == 1){
                    var_window = 'corregedoria.inspection.inspection.WindowExecutionOrgan';
                }
                else {
                    if (selected.data.inspection_type == 2){
                        var_window = 'corregedoria.inspection.inspection.WindowEspecialGroup';
                    }
                    else {
                        if (selected.data.inspection_type == 3){
                            var_window = 'corregedoria.inspection.inspection.WindowAuxiliaryOrgan';
                        }
                    }
                }
                Ext._create(var_window, {
                    action: 'update',
                    oId: selected.get('pk'),
                    values: selected.data,
                }).show();
            }
        } else {
            console.log('sem difinição para o órgão de exercucao.');
        }
    },

    getFillingAction: function() {
        if(!this._fillingAction){
            this._fillingAction = new Ext.Button({
                xtype: 'button',
                text: 'Relatório de Inspeção/Correição',
                iconCls: 'icon-crgmpe icon-crgmpe-book',
                menu: [
                    {
                        text: 'Nova Inspeção/Correição em',
                        iconCls: 'icon-crgmpe icon-crgmpe-add',
                        scope: this,
                        menu: [
                            {
                                text: 'Órgão de Execução',
                                iconCls: 'icon-crgmpe icon-crgmpe-house',
                                scope: this,
                                handler: function() {
                                    this.createInspection(1);
                                },
                            },
                            {
                                text: 'Grupo Especial',
                                iconCls: 'icon-crgmpe icon-crgmpe-users',
                                scope: this,
                                handler: function() {
                                    this.createInspection(2);
                                }
                            },
                            {
                                text: 'Órgão Auxiliar',
                                iconCls: 'icon-crgmpe icon-crgmpe-tool',
                                scope: this,
                                handler: function() {
                                    this.createInspection(3);
                                }
                            },
                        ]
                    },
                    '-',
                    {
                        text: 'Preencher',
                        iconCls: 'icon-crgmpe icon-crgmpe-edit-paper',
                        scope: this,
                        // handler: function() {
                        //     this.getFilling();
                        // },
                        menu: [
                            {
                                text: 'Órgão de Execução',
                                iconCls: 'icon-crgmpe icon-crgmpe-house',
                                scope: this,
                                // handler: function() {
                                //     this.getFilling();
                                // },
                                menu: [
                                  {
                                      text: 'Primeira Instância',
                                      iconCls: 'icon-crgmpe icon-crgmpe-man-blue',
                                      scope: this,
                                      // handler: function() {
                                      //     this.getFilling();
                                      // },
                                      menu: [
                                          {
                                              text: 'Regularidade dos Serviços',
                                              iconCls: 'icon-crgmpe icon-crgmpe-confirmed',
                                              scope: this,
                                              handler: function() {
                                                  this.getFilling('regularityofservices');
                                              }
                                          },
                                          {
                                              text: 'Estutura',
                                              iconCls: 'icon-crgmpe icon-crgmpe-house',
                                              scope: this,
                                              handler: function() {
                                                  this.getFilling('structure');
                                              }
                                          },
                                          {
                                              text: 'Desempenho Funcional',
                                              iconCls: 'icon-crgmpe icon-crgmpe-up-graph',
                                              scope: this,
                                              handler: function() {
                                                  this.getFilling('functionalperformance');
                                              }
                                          },
                                          {
                                              text: 'Observações Gerais',
                                              iconCls: 'icon-crgmpe icon-crgmpe-open-bookmark',
                                              scope: this,
                                              handler: function() {
                                                  this.getFilling('generalobservations');
                                              }
                                          },
                                          {
                                              text: 'Recomendações',
                                              iconCls: 'icon-crgmpe icon-crgmpe-arrows',
                                              scope: this,
                                              handler: function() {
                                                  this.getFilling('recommendations');
                                              }
                                          },
                                          {
                                              text: 'Anexos',
                                              iconCls: 'icon-crgmpe icon-crgmpe-attachment',
                                              scope: this,
                                              handler: function() {
                                                  this.getFilling('attachments');
                                              }
                                          },
                                      ]
                                    },
                                    {
                                        text: 'Segunda Instância',
                                        iconCls: 'icon-crgmpe icon-crgmpe-man-black',
                                        scope: this,
                                        // handler: function() {
                                        //     this.getFilling();
                                        // },
                                        menu: [
                                            {
                                                text: 'Controle de Atividades',
                                                iconCls: 'icon-crgmpe icon-crgmpe-calendar-plus',
                                                scope: this,
                                                handler: function() {
                                                    this.getFilling('procuratorate');
                                                }
                                            },
                                            {
                                                text: 'Estutura',
                                                iconCls: 'icon-crgmpe icon-crgmpe-house',
                                                scope: this,
                                                handler: function() {
                                                    this.getFilling('structure');
                                                }
                                            },
                                            {
                                                text: 'Observações Gerais',
                                                iconCls: 'icon-crgmpe icon-crgmpe-open-bookmark',
                                                scope: this,
                                                handler: function() {
                                                    this.getFilling('generalobservations');
                                                }
                                            },
                                            {
                                                text: 'Anexos',
                                                iconCls: 'icon-crgmpe icon-crgmpe-attachment',
                                                scope: this,
                                                handler: function() {
                                                    this.getFilling('attachments');
                                                }
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                text: 'Grupo Especial',
                                iconCls: 'icon-crgmpe icon-crgmpe-users',
                                scope: this,
                                // handler: function() {
                                //     this.getFilling();
                                // },
                                menu: [
                                    {
                                        text: 'Dados Gerais',
                                        iconCls: 'icon-crgmpe icon-crgmpe-select',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('generaldata');
                                        }
                                    },
                                    {
                                        text: 'Estutura de Funcionametno',
                                        iconCls: 'icon-crgmpe icon-crgmpe-edit-paper',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('operatingstructure');
                                        }
                                    },
                                    {
                                        text: 'Organização Administrativa',
                                        iconCls: 'icon-crgmpe icon-crgmpe-list',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('administrativeorganization');
                                        }
                                    },
                                    {
                                        text: 'Atuação',
                                        iconCls: 'icon-crgmpe icon-crgmpe-witness',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('performance');
                                        }
                                    },
                                    {
                                        text: 'Observações Gerais',
                                        iconCls: 'icon-crgmpe icon-crgmpe-open-bookmark',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('generalobservations');
                                        }
                                    },
                                    {
                                        text: 'Recomendações',
                                        iconCls: 'icon-crgmpe icon-crgmpe-arrows',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('recommendations');
                                        }
                                    },
                                    {
                                        text: 'Anexos',
                                        iconCls: 'icon-crgmpe icon-crgmpe-attachment',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('attachments');
                                        }
                                    },
                                ]
                            },
                            {
                                text: 'Órgão Auxiliar',
                                iconCls: 'icon-crgmpe icon-crgmpe-tool',
                                scope: this,
                                // handler: function() {
                                //     this.getFilling();
                                // },
                                menu: [
                                    {
                                        text: 'Dados Gerais',
                                        iconCls: 'icon-crgmpe icon-crgmpe-select',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('generaldata');
                                        }
                                    },
                                    {
                                        text: 'Estutura de Funcionametno',
                                        iconCls: 'icon-crgmpe icon-crgmpe-edit-paper',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('operatingstructure');
                                        }
                                    },
                                    {
                                        text: 'Organização Administrativa',
                                        iconCls: 'icon-crgmpe icon-crgmpe-list',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('administrativeorganization');
                                        }
                                    },
                                    {
                                        text: 'Atuação',
                                        iconCls: 'icon-crgmpe icon-crgmpe-witness',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('performance');
                                        }
                                    },
                                    {
                                        text: 'Observações Gerais',
                                        iconCls: 'icon-crgmpe icon-crgmpe-open-bookmark',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('generalobservations');
                                        }
                                    },
                                    {
                                        text: 'Recomendações',
                                        iconCls: 'icon-crgmpe icon-crgmpe-arrows',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('recommendations');
                                        }
                                    },
                                    {
                                        text: 'Anexos',
                                        iconCls: 'icon-crgmpe icon-crgmpe-attachment',
                                        scope: this,
                                        handler: function() {
                                            this.getFilling('attachments');
                                        }
                                    },
                                ]
                            },
                        ],
                    },
                    '-',
                    {
                        text: 'Assinar',
                        iconCls: 'icon-crgmpe icon-crgmpe-man-changed',
                        scope: this,
                        handler: function() {
                            this.sign();
                        }
                    },
                    '-',
                    {
                        text: 'Remeter ao Órgão Inspecionado',
                        iconCls: 'icon-crgmpe icon-crgmpe-send-mail',
                        scope: this,
                        handler: function() {
                            this.communication();
                        }
                    },
                    {
                        text: 'Remeter ao CPJ / CSMP',
                        iconCls: 'icon-crgmpe icon-crgmpe-send-mail',
                        scope: this,
                        handler: function() {
                            this.openCommunicationCPJCSMPWindow();
                        }
                    },
                    '-',
                    {
                        text: 'Finalizar Inspeção/Correição',
                        iconCls: 'icon-crgmpe icon-crgmpe-read-only',
                        scope: this,
                        handler: function() { this.finalize();  }
                    },
                    '-',
                    {
                        text: 'Download',
                        iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                        menu: [
                          {
                              text: 'Relatório de Inspeção/Correição (PDF)',
                              iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                              scope: this,
                              handler: function() { this.getInspectionReport(); }
                          },
                          '-',
                          {
                              text: 'Histórico de Inspeções',
                              iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                              scope: this,
                              handler: this.openHistoryInspectionReport
                          },
                          '-',
                          {
                              text: 'Anexos da Inspeção/Correição (ZIP))',
                              iconCls: 'icon-crgmpe icon-crgmpe-application-x-gzip',
                              disabled: true,
                              scope: this,
                              handler: function() {  }
                          }
                        ]
                    },
                    '-',
                    {
                        text: 'Avançado',
                        iconCls: 'icon-crgmpe icon-crgmpe-settings',
                        menu: [
                            {
                                text: 'Recarregar dados da Inspeção (RH, RDIR, SIACMP, e-EXT, RAF)',
                                iconCls: 'icon-crgmpe icon-crgmpe-refresh',
                                scope: this,
                                handler: function() { this.reload_data();  }
                            },
                            {
                                text: 'Recarregar apenas Endereço',
                                iconCls: 'icon-crgmpe icon-crgmpe-refresh',
                                scope: this,
                                handler: function() { this.reload_data('address');  }
                            },
                            {
                                text: 'Recarregar quantitativos de Processos',
                                iconCls: 'icon-crgmpe icon-crgmpe-refresh',
                                scope: this,
                                handler: function() { this.reload_data('lawsuit');  }
                            },
                            {
                                text: 'Recarregar apenas Estrutura de Pessoal',
                                iconCls: 'icon-crgmpe icon-crgmpe-refresh',
                                scope: this,
                                handler: function() { this.reload_data('employees');  }
                            },
                            {
                                text: 'Recarregar apenas Acumulações',
                                iconCls: 'icon-crgmpe icon-crgmpe-refresh',
                                scope: this,
                                handler: function() { this.reload_data('accumulates');  }
                            }
                        ]
                    },
                ]
            });
        }
        return this._fillingAction;
    },

    getFilling: function(var_frame) {
        var selected = this.getSelectionModel().getSelected();
        var rest = Ext._create('raf.functionalactivityreport.Restful');
        if(selected) {
            var var_window = '';
            if (selected.data.inspection_type) {
                if (selected.data.inspection_type == 1) {
                    var_window = selected.data.execution_organ_instance == 1 ? 'corregedoria.inspection.inspection.filling.Launcher_executionorgan_prosecution' : 'corregedoria.inspection.inspection.filling.Launcher_executionorgan_procuratorate';
                }
                if (selected.data.inspection_type == 2) {
                    var_window = 'corregedoria.inspection.inspection.filling.Launcher_especialgroup';
                }
                if (selected.data.inspection_type == 3) {
                    var_window = 'corregedoria.inspection.inspection.filling.Launcher_auxiliaryorgan';
                }
                Ext._create(var_window, {
                    values: {
                        inspection_id: selected.data.pk,
                        employee: selected.data.employee_unicode,
                        responsible: selected.data.responsible_unicode,
                        execution_organ: selected.data.execution_organ_unicode,
                        inspector_general: selected.data.inspector_general_unicode,
                        inspector_prosecutor: selected.data.inspector_prosecutor_unicode,
                        inspection_date_initial: selected.data.inspection_date_initial_formatted,
                        inspection_date_final: selected.data.inspection_date_final_formatted,
                        electoral_applicable: selected.data.electoral_applicable,
                        gridInspection: this,
                        final_score: selected.data.final_score,
                        instance: selected.data.execution_organ_instance,
                        frame: var_frame,
                        var_structuregeneralstatus: selected.data.structuregeneralstatus,
                        var_administrativeorganizationgeneralstatus: selected.data.administrativeorganizationgeneralstatus,
                        var_registration_type: selected.data.registration_type,
                    },
                }).show();
            } else {
                Ext.Msg.show({
                    title: 'Preencher Inspeção/Correição',
                    msg: 'Inspeção sem definição de tipo.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        } else {
            Ext.Msg.show({
                title: 'Preencher Inspeção/Correição',
                msg: 'Primeiro selecione a Inspeção/Correição que deseja preencher.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getViewReportAction: function() {
        if(!this._viewReportAction){
            this._viewReportAction = new Ext.Button({
                text: '<b>Relatório de Inspeção/Correição</b>',
                iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                scope: this,
                handler: function() {
                    var selected = this.getSelectionModel().getSelected();
                    if (selected) {
                        var var_report = '';
                        if (selected.data.inspection_type) {
                            if (selected.data.inspection_type == 1) {
                                var_report = selected.get('execution_organ_instance') == 1 ? '/to/mpe/corregedoria/inspection/inspection_report' : '/to/mpe/corregedoria/inspection/inspection_report_procuratorate';
                            }
                            if (selected.data.inspection_type == 2) {
                                var_report = '/to/mpe/corregedoria/inspection/inspection_report_especialgroup';
                            }
                            if (selected.data.inspection_type == 3) {
                                var_report = '/to/mpe/corregedoria/inspection/inspection_report_auxiliarorgan';
                            }

                            engine.mq.Report.request({
                                report: var_report,
                                waitMessage: 'Gerando os relatório...',
                                params: {
                                    outfile: 'relatorio-inspecao-'+selected.get('execution_organ_slugify'),
                                    report_name: 'Relatório de Inspeção - '+selected.get('execution_organ_unicode'),
                                    inspection: selected.get('pk'),
                                    all: selected.get('employee') == selected.get('atual_employee') ? '1' : '0',
                                }
                            });
                        } else {
                            Ext.Msg.show({
                                title: 'Preencher Inspeção/Correição',
                                msg: 'Inspeção sem definição de tipo.',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    } else {
                      Ext.Msg.show({
                          title: 'Relatórios',
                          msg: 'Primeiro selecione a inspeção/correição para geração do relatório.',
                          icon: Ext.Msg.ERROR,
                          buttons: Ext.Msg.OK
                      });
                    }
                }
            });
        }
        return this._viewReportAction;
    },

    sign: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if (selected.data.inspector_general_bool || selected.data.inspector_prosecutor_bool) {
                console.log(selected.data);
                Ext._create('corregedoria.inspection.inspection.sign.Window', {
                    values: {
                        inspection_id: selected.data.pk,
                        employee_name: selected.data.employee_unicode,
                        responsible: selected.data.responsible_unicode,
                        execution_organ: selected.data.execution_organ_unicode,
                        inspection_date_initial: selected.data.inspection_date_initial_formatted,
                        inspection_date_final: selected.data.inspection_date_final_formatted,
                        electoral_applicable: selected.data.electoral_applicable,
                        gridInspection: this,
                        final_score: selected.data.final_score,
                        inspector_general: selected.data.inspector_general_unicode,
                        inspector_general_bool: selected.data.inspector_general_bool,
                        inspector_prosecutor: selected.data.inspector_prosecutor_unicode,
                        employee: selected.data.inspector_prosecutor_pk,
                        inspector_prosecutor_bool: selected.data.inspector_prosecutor_bool,
                    },
                }).show();
            } else {
                Ext.Msg.show({
                    title: 'Assinar Inspeção/Correição',
                    msg: 'Usuário não vinculado a Inspeção/Correição.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        } else {
            Ext.Msg.show({
                title: 'Assinar Inspeção/Correição',
                msg: 'Primeiro selecione a Inspeção/Correição que deseja assinar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getSignAction: function() {
        if(!this._signAction){
            this._signAction = new Ext.Button({
                text: 'Assinar',
                scope: this,
                iconCls: 'icon-crgmpe icon-crgmpe-man-changed',
                handler: function() {
                    this.sign();
                }
            });
        }
        return this._signAction;
    },

    openCommunicationCPJCSMPWindow: function() {
        Ext._create('corregedoria.inspection.inspection.SendCommunicationCPJCSMP', {
            values: {
                gridInspection: this,
            },
        }).show();
    },

    communication_cpjcsmp: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            var values = {inspection: selected.get('pk'), };
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Remetendo dados da inspeção...'});
            Ext.Msg.show({
                title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                msg: 'Tem certeza que deseja remeter a inspeção ao CPJ e ao CSMP?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('INSPECTIONInspection', 'communication_cpjcsmp'),
                        callback: function() {
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                                this.getStore().reload();
                            } else {
                                Ext.Msg.show({
                                    title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: values,
                    });
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Remeter Inspeção/Correição ao CPJ e ao CSMP',
                msg: 'Primeiro selecione a Inspeção/Correição que deseja remeter.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    communication: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            var values = {inspection: selected.get('pk'), };
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Remetendo dados da inspeção...'});
            Ext.Msg.show({
                title: 'Remeter Inspeção/Correição ao Órgão Inspecionado',
                msg: 'Tem certeza que deseja remeter a inspeção ap órgão inspecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('INSPECTIONInspection', 'communication'),
                        callback: function() {
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Remeter Inspeção/Correição ao Órgão Inspecionado',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                                this.getStore().reload();
                            } else {
                                Ext.Msg.show({
                                    title: 'Remeter Inspeção/Correição ao Órgão Inspecionado',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Remeter Inspeção/Correição ao Órgão Inspecionado',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: values,
                    });
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Remeter Inspeção/Correição ao Órgão Inspecionado',
                msg: 'Primeiro selecione a Inspeção/Correição que deseja remeter.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getCommunicationAction: function() {
        if(!this._communicationAction){
            this._communicationAction = new Ext.Button({
                text: 'Remeter ao Órgão de Execução',
                scope: this,
                iconCls: 'icon-crgmpe icon-crgmpe-send-mail',
                handler: function() {
                    this.communication();
                }
            });
        }
        return this._communicationAction;
    },

    getReportAction: function() {
        if(!this._reportAction){
            this._reportAction = new Ext.Button({
                xtype: 'button',
                text: 'Gerar PDF',
                iconCls: 'icon-crgmpe icon-crgmpe-reports',
            });
        }
        return this._reportAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 90, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Início', dataIndex: 'inspection_date_initial', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 70},
                    {header: 'Fim', dataIndex: 'inspection_date_final', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 70},
                    {header: 'Órgão Inspecionado', dataIndex: 'execution_organ_unicode', id: 'autoExpandColumn'},
                    {header: 'Procurador/Promotor', dataIndex: 'employee_unicode', width: 350},
                    {header: 'Operosidade', dataIndex: 'operability_score', width: 80, align: 'center', visible: false},
                    {header: 'Presteza', dataIndex: 'promptness_score', width: 80, align: 'center', visible: false},
                    {header: 'Nota Final', dataIndex: 'final_score', width: 80, align: 'center', visible: false},
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {

            }
        );
        corregedoria.inspection.inspection.Grid.superclass.constructor.call(this, cfg);
    }
});
core.RestfulGrid.register(
    'corregedoria.inspection.inspection.Restful',
    'corregedoria.inspection.inspection.Grid'
);
