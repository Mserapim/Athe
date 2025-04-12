

Ext._define('rh.falta.RelatorioWindow', {
    extend: 'Ext.Window',

    PDF_RELATORIO: 'generate_report_pdf',
    CSV_RELATORIO: 'generate_report_csv',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getServidor(cfg),
                    this.getTipoFalta(cfg),
                    this.getSituacao(cfg),
                    this.getImpactoFinanceiro(cfg),
                    this.getCompetenciaDesconto(cfg),
                    this.getOriginCheckboxGrid(cfg),
                    {
                        xtype: 'fieldset',
                        title: 'Período do Processamento',
                        width: 450,
                        layout: 'hbox',
                        items: [
                            {
                                xtype:'panel',
                                layout:'form',
                                labelAlign:'top',
                                flex:'1',
                                width:150,
                                items:[
                                    this.getProceDataInicio(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout:'form',
                                labelAlign:'top',
                                flex:'1',
                                width:150,
                                items:[
                                    this.getProceDataFim(cfg),
                                ]
                            }
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Período da Falta',
                        width: 450,
                        layout: 'hbox',
                        items: [
                            {
                                xtype:'panel',
                                layout:'form',
                                labelAlign:'top',
                                flex:'1',
                                width:150,
                                items:[
                                    this.getFaltaDataInicio(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout:'form',
                                labelAlign:'top',
                                flex:'1',
                                width:150,
                                items:[
                                    this.getFaltaDataFim(cfg),
                                ]
                            }
                        ]
                    },
                ]
                    
            });
        return this._formPanel;
    },

    getServidor: function(cfg) {
        if(!this._servidor)
            this._servidor = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Servidor(a)",
                allowBlank: true,
                rest: "rh.employee.Restful",
                name: "servidor",
                width:350,
                value: (cfg.params.servidor != undefined ? cfg.params.servidor : '')
            });

        return this._servidor;
    },

    getTipoFalta: function(cfg) {
        if(!this._tipoFalta)
            this._tipoFalta = Ext._create('core.fields.ComboField', {
                width: 350,
                hiddenName: 'tipo_falta',
                fieldLabel: 'Tipo de Falta',
                store: [
                    [ 1, 'JUSTIFICADA'],
                    [ 2, 'INJUSTIFICADA'],
                ],
                triggerAction: 'all',
            });

        return this._tipoFalta;
    },

    getSituacao: function(cfg) {
        if(!this.situacao)
            this.situacao = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Situação',
                name: 'situacao',
                hiddenName: 'situacao',
                choiceId: 'ponto.SITUATION_CHOICES',
                allowBlank: true,
                width: 350,
                triggerAction: 'all',
            });

        return this.situacao;
    },

    getImpactoFinanceiro: function(cfg) {
        if(!this._impactoFinanceiro)
            this._impactoFinanceiro = Ext._create('core.fields.ComboField', {
                width: 350,
                hiddenName: 'impacto_financeiro',
                fieldLabel: 'Impacto Financeiro',
                store: [
                    [ 1, 'COM IMPACTO'],
                    [ 2, 'SEM IMPACTO'],
                ],
                triggerAction: 'all',
            });

        return this._impactoFinanceiro;
    },
    
    getCompetenciaDesconto: function(cfg) {
        if(!this._competenciaDesconto)
            this._competenciaDesconto = Ext._create('Ext.form.DateField', {
                width: 350,
                hiddenName: 'competencia_desconto',
                fieldLabel: 'Competência de Desconto (mm/aaaa)',
                format: 'm/Y',
            });

        return this._competenciaDesconto;
    },

    getOriginCheckboxGrid: function () {
        if (!this._multiReportGrid) {
            var selectionModel = new Ext.grid.CheckboxSelectionModel({ checkOnly: true });
            this._multiReportGrid = Ext._create('Ext.grid.GridPanel', {
                fieldLabel: 'Tipos de Servidores',
                sm: selectionModel,
                deferRowRender: false,
                stripRows: true,
                style: { border: '1px solid #99bbe8' },
                columnLines: true,
                height: 250,
                width: 350,
                autoExpandColumn: 'description',
                checked: true,
                store: Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('PONTRelatorioFalta', 'employee_type_by_possessions')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            { name: 'value', type: 'string' },
                            { name: 'description', type: 'string' }
                        ]
                    })
                }),
                columns: [
                    selectionModel,
                    { header: 'Sigla', dataIndex: 'value', hidden: true, width: 50 },
                    { header: 'Tipos', dataIndex: 'description', id: 'description' },
                ],
                
            });
        }
        this._multiReportGrid.getStore().on({
            scope: this,
            load: function () {
                this.markAll(this._multiReportGrid);
            }
        });

        return this._multiReportGrid;
    },

    markAll: function (grid) {
        var _data = grid.getStore().data;
        var _selected = [];
        for (i = 0; i <= _data.length; i++) {
            _data.items.map(function (item) {
                    _selected.push(item)
            });
        }
        grid.getSelectionModel().clearSelections();
        grid.getSelectionModel().selectRecords(_selected);
    },

    getProceDataInicio: function(cfg) {
        if(!this._proceDataInicio)
            this._proceDataInicio = Ext._create('Ext.form.DateField', {
                hiddenName: 'processamento_data_inicio',
                fieldLabel: 'Início',
                allowBlank: true,
            });

        return this._proceDataInicio;
    },

    getProceDataFim: function(cfg) {
        if(!this._proceDataFim)
            this._proceDataFim = Ext._create('Ext.form.DateField', {
                hiddenName: 'processamento_data_fim',
                fieldLabel: 'Fim',
                allowBlank: true,
            });

        return this._proceDataFim;
    },

    getFaltaDataInicio: function(cfg) {
        if(!this._faltaDataInicio)
            this._faltaDataInicio = Ext._create('Ext.form.DateField', {
                hiddenName: 'falta_data_inicio',
                fieldLabel: 'Início',
                allowBlank: true,
            });

        return this._faltaDataInicio;
    },

    getFaltaDataFim: function(cfg) {
        if(!this._faltaDataFim)
            this._faltaDataFim = Ext._create('Ext.form.DateField', {
                hiddenName: 'falta_data_fim',
                fieldLabel: 'Fim',
                allowBlank: true,
            });

        return this._faltaDataFim;
    },

    gerarRelatorio: function(tipo_relatorio){
        var form = this.getFormPanel().getForm();
        var proce_dt_inicio = ''
        var proce_dt_fim = ''
        var falta_dt_inicio = ''
        var falta_dt_fim = ''
        var competencia_desconto = ''

        if (this.getProceDataInicio().getValue() != '') {
            proce_dt_inicio = this.getProceDataInicio().getValue().format('Y-m-d')
        }
        if (this.getProceDataFim().getValue() != '') {
            proce_dt_fim = this.getProceDataFim().getValue().format('Y-m-d')
        }
        if (this.getFaltaDataInicio().getValue() != '') {
            falta_dt_inicio = this.getFaltaDataInicio().getValue().format('Y-m-d')
        }
        if (this.getFaltaDataFim().getValue() != '') {
            falta_dt_fim = this.getFaltaDataFim().getValue().format('Y-m-d')
        }
        if (this.getCompetenciaDesconto().getValue() != '') {
            competencia_desconto = this.getCompetenciaDesconto().getValue().format('m/Y')
        }

        var params = {
            servidor: this.getServidor().getValue(),
            tipo_falta: this.getTipoFalta().getValue(),
            situacao: this.getSituacao().getValue(),
            impacto_financeiro: this.getImpactoFinanceiro().getValue(),
            competencia_desconto: competencia_desconto,
            proce_data_inicio: proce_dt_inicio,
            proce_data_fim: proce_dt_fim,
            falta_data_inicio: falta_dt_inicio,
            falta_data_fim: falta_dt_fim,
        };
        
        selections = this.getOriginCheckboxGrid().getSelectionModel().getSelections();
        params.types_by_possession = selections.map(function (selection) {
            return selection.data.value;
        }).join(',');
    
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
               'PONTRelatorioFalta', 
               tipo_relatorio
            ),
            params: params,
            scope: this,
            success: function (request) {
                var obj = Ext.decode(request.responseText);
                if (obj.success){
                    Ext.Msg.show({
                        title: 'Solicitando Relatório',
                        msg: obj.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    this.destroy();
                }else{
                    Ext.Msg.show({
                        title: 'Error',
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }     
            },
            failure: function (request) {
                Ext.Msg.show({
                    msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                })
            },
            scope: this
        });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
        	cfg,
        	{
        		title: 'Relatório de Falta',
        		closable: true,
				height: 700,
        		width: 500
        	}
        );
		Ext.apply(
			cfg,
			{
				border: false,
				layout: 'fit',
				items: [
					this.getFormPanel(cfg)
				],
                buttons: [
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        text: 'Gerar Relatório',
                        width: 100,
                        height: 25,
                        scope: this,
                        menu: {
                            scope: this,
                            items: [
                                {
                                    text: 'Arquivo PDF ',
                                    type: 'PDF',
                                    iconCls: 'icon-ged icon-ged-application-pdf',
                                    scope: this,
                                    handler: function(item) {
                                        this.gerarRelatorio(this.PDF_RELATORIO);
                                    }
                                },
                                {
                                    text: 'Arquivo CSV',
                                    type: 'CSV',
                                    iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                    scope: this,
                                    handler: function(item) {
                                        this.gerarRelatorio(this.CSV_RELATORIO);
                                    }
                                },
                            ]
                        }
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]   
			}
		);
		rh.falta.RelatorioWindow.superclass.constructor.call(this, cfg);
    }
});