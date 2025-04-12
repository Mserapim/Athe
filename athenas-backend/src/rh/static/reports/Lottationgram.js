/**
 *
 **/

Ext._define('rh.reports.Lottationgram', {
	extend: 'toolkit.widget.TabPanel',

    REPORT_CLASS: 'RHLottationgramReport',
    PDF_FUNCTION: 'generate_report_pdf',
    CSV_FUNCTION: 'generate_report_csv',

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
                anchor: '99%',
                autoExpandColumn: 'description',
                checked: true,
                store: Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('RHLottationgramReport', 'employee_type_by_possessions')
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

        console.log(this._multiReportGrid)
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

    getCounty: function(){
		if(!this._county)
			this._county = Ext._create('core.fields.AutocompleteField', {
                name: 'county',
                rest: 'rh.localidade.Restful',
                fieldLabel: 'Município',
                width: 450,
                gridConfig: {
                    configOrderToolBar: ['search', '->'],
                    hideColumns: [
                        'valor_vale_transporte',
                        'ibge',
                        'distancia_capital',
                        'microregiao_unicode',
                        'sede_termo',
                        'siafi',
                        'cep',
                        'indicador_municipio',
                        'sigla',
                        'descricao',
                    ],
                    columnAction: false,
                },
                preFilter: [
                    { property: 'estado', value: 79, stage: 100 },
                ]
			});

		return this._county;
	},

    getNucleo: function(cfg) {
        if(!this._nucleo)
            this._nucleo = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Núcleo',
                name: 'nucleo',
                hiddenName: 'nucleo',
                choiceId: 'rh.NUCLEO_CHOICES',
                allowBlank: true,
                width: 450
            });

        return this._nucleo;
    },

	getWorkplace: function(){
		if(!this._workplace)
			this._workplace = Ext._create('core.fields.AutocompleteField', {
                name: 'workplace',
                rest: 'rh.workplace.Restful',
                fieldLabel: 'Lotação / Designação',
                width: 450
			});

		return this._workplace;
	},

    getIncludeCounties: function() {
        if (!this._includeCounties) 
            this._includeCounties = Ext._create('Ext.form.Checkbox', {
            boxLabel: 'Buscar por todos os municípios da comarca onde se localiza o município selecionado.',
            checked: false,
            scope: this,
            triggerAction: 'all',
            style: { textAlign: 'left', }
        });

        return this._includeCounties;
    },
	
	getJobPosition: function(){
		if(!this._jobposition)
			this._jobposition = Ext._create('core.fields.AutocompleteField', {
                name: 'jobposition',
                rest: 'rh.jobposition.Restful',
                fieldLabel: 'Cargo',
                width: 450
			});

		return this._jobposition;
	},

    getEmployeeField: function(){
		if(!this._employeefield)
			this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 450
			});

		return this._employeefield;
	},

    getCompetenceField: function(config){
        if(!this.competenceField)
            this.competenceField = Ext._create('Ext.form.TextField', {
                name: 'competencia',
                fieldLabel: 'Competência (mm/aaaa)',
                width: 450,
            }, config);

        return this.competenceField;
    },


    _lotacionogramReport: function(report_function){
        var params = {
            cargo:  this.getJobPosition().getValue(),
            lotacao: this.getWorkplace().getValue(),
            nucleo: this.getNucleo().getValue(),
            municipio: this.getCounty().getValue(),
            comarca: this.getIncludeCounties().getValue(),
            servidor: this.getEmployeeField().getValue(),
            competencia: this.getCompetenceField().getValue(),
        };

        selections = this.getOriginCheckboxGrid().getSelectionModel().getSelections(),
        params.types_by_possession = selections.map(function (selection) {
            return selection.data.value;
        }).join(',');
        
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
               this.REPORT_CLASS, 
               report_function
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

	getMain: function(){
		if(!this._panel)
		this._panel = new Ext.Panel({
		    layout: 'border',
		    region: 'center',
		    height: 650,
		    split: true,
		    autoEl: {tag: 'center'},
		    items: [
	        {
	        	region: 'center',
	        	border: false,
				autoScroll: true,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Relatório Lotacionograma',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
                        this.getCompetenceField(),
                        this.getEmployeeField(),
						this.getCounty(),
                        this.getIncludeCounties(),
                        this.getNucleo(),
                        this.getWorkplace(),
						this.getJobPosition(),
						this.getOriginCheckboxGrid(),
						{
							xtype: 'button',
							iconCls: 'icon-siatu icon-siatu-move-down',
							style: 'margin-top: 10px',
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
                                        handler: function (item) {
											this._lotacionogramReport(this.PDF_FUNCTION)
										}
									},
									{
										text: 'Arquivo CSV',
										type: 'CSV',
										iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
										scope: this,
										handler: function (item) {
											this._lotacionogramReport(this.CSV_FUNCTION)
										}
									},
								]
							},
						}
	        		]
	        	},
        		]
        	}
    		]
	    });

		return this._panel;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Relatório -> Lotacionograma'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[ 
					this.getMain(),
				]
			}
		);

		// this.getCurrentPayroll();

		rh.reports.Lottationgram.superclass.constructor.call(this, cfg);
	}
});