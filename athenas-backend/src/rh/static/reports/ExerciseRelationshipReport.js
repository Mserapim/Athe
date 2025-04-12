/**
 *
 **/

Ext._define('rh.reports.ExerciseRelationshipReport', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(file_type){

	    var employee = this.getEmployeeField().getValue();
	    var start_month = this.getInitialMonth().getValue();
	    var end_month = this.getEndMonth().getValue();
	    var start_year = this.getInitialYear().getValue();
	    var end_year = this.getEndYear().getValue();
	    var year = this.getYear().getValue();

	    engine.mq.Report.request({
	        report: '/to/mpe/expediente/exercises_relationship_substitution_removal',
	        waitMessage: 'Gerando relatório...',
	        params: {

	            outfile: 'exercicios',
	            report_name: 'Relatório de Exercícios',
	            membro: employee,
	            mes_inicial: start_month,
	            ano_inicial: start_year,
	            mes_final: end_month,
	            ano_final: end_year,
	            anual: year
	        }

	    }, file_type);
    },

    getEmployeeField: function(){
		if(!this._employeefield)
			this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Membro',
                preFilter: [
                  {property: 'ativo', value: true, stage: 1},
                  {property: 'tipo', value: 'M', stage: 2}
              	],
                width: 350
			});

		return this._employeefield;
	},

	getInitialMonth: function () {
        if (!this._monthInitialField) {
            this._monthInitialField = new Ext.form.ComboBox({
                fieldLabel: 'Mês Inicial',
                anchor: '99%',
                store: [
                    [1, 'JANEIRO'],
                    [2, 'FEVEREIRO'],
                    [3, 'MARÇO'],
                    [4, 'ABRIL'],
                    [5, 'MAIO'],
                    [6, 'JUNHO'],
                    [7, 'JULHO'],
                    [8, 'AGOSTO'],
                    [9, 'SETEMBRO'],
                    [10, 'OUTUBRO'],
                    [11, 'NOVEMBRO'],
                    [12, 'DEZEMBRO'],
                ],
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._monthInitialField;
    },

	getEndMonth: function () {
        if (!this._monthEndField) {
            this._monthEndField = new Ext.form.ComboBox({
                fieldLabel: 'Mês Final',
                anchor: '99%',
                store: [
                    [1, 'JANEIRO'],
                    [2, 'FEVEREIRO'],
                    [3, 'MARÇO'],
                    [4, 'ABRIL'],
                    [5, 'MAIO'],
                    [6, 'JUNHO'],
                    [7, 'JULHO'],
                    [8, 'AGOSTO'],
                    [9, 'SETEMBRO'],
                    [10, 'OUTUBRO'],
                    [11, 'NOVEMBRO'],
                    [12, 'DEZEMBRO'],
                ],
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._monthEndField;
    },

    getInitialYear: function(cfg) {
        if(!this._initialYear)
            this._initialYear = Ext._create('Ext.form.NumberField', {
                xtype: 'numberfield',
                fieldLabel: 'Ano Inicial',
                width: 100
            });

        return this._initialYear;
    },

    getEndYear: function(cfg) {
        if(!this._endYear)
            this._endYear = Ext._create('Ext.form.NumberField', {
                xtype: 'numberfield',
                fieldLabel: 'Ano Final',
                width: 100
            });

        return this._endYear;
    },

    getYear: function(cfg) {
        if(!this._year)
            this._year = Ext._create('Ext.form.NumberField', {
                xtype: 'numberfield',
                fieldLabel: 'Ano',
                width: '90%'
            });

        return this._year;
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
	        	// title: 'Informações do Contra-Cheque',
	        	region: 'center',
	        	border: false,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Relatório >> Exercícios',
	        		name: 'fieldServidor',
	        		width: 500,
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        			{
	        				xtype: 'fieldset',
	        				title: 'Servidor',
	        				items: this.getEmployeeField()
	        			},
	        			{
	        				xtype: 'fieldset',
	        				title: 'Por Período',
	        				items: [
	        				{
	        					layout: 'hbox',
	        					border: false,
	        				    defaults: {flex: 1, layout: 'form', border: false},
		        				items: [
		        				{
		        					items:[
		        						this.getInitialMonth()
	        						]
		        				},
		        				{
		        					items:[
		        						this.getInitialYear()	
		        					]
		        				}
		        				]
		        			},
		        			{
	        					layout: 'hbox',
	        					border: false,
	        				    defaults: {flex: 1, layout: 'form', border: false},
		        				items: [
		        				{
		        					items:[
		        						this.getEndMonth()
	        						]
		        				},
		        				{
		        					items:[
		        						this.getEndYear()	
		        					]
		        				}
		        				]
		        			},
	        				]
	        			},
	        			{
	        				xtype: 'fieldset',
	        				title: 'Por Ano',
	        				items: this.getYear()
	        			},
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
                                            this._buildReport(item.type);
                                        }
                                    },
                                    {
                                        text: 'Arquivo ODT',
                                        type: 'ODT',
                                        iconCls: 'icon-ged icon-ged-application-msword',
                                        scope: this,
                                        handler: function (item) {
                                            this._buildReport(item.type);
                                        }
                                    },
                                    {
                                        text: 'Arquivo XLS',
                                        type: 'XLS',
                                        iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                        scope: this,
                                        handler: function (item) {
                                            this._buildReport(item.type);
                                        }
                                    },
                                ]
                            },
                        },
                    {
                    	xtype: 'displayfield',
                    	value: '* Todos os campos são opcionais',
                    	hideLabel: true,
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
			   title: 'Relatório -> Exercícios'
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

		
	rh.reports.ExerciseRelationshipReport.superclass.constructor.call(this, cfg);
	}
});