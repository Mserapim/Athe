Ext._define('rh.reports.ReportMemberActivitiesMonth', {

    extend: 'toolkit.widget.TabPanel',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                items: this._getDocumentsFields(cfg)
            });

        return this._formPanel;
    },

    getRangeOfYears: function () {
        var years = [];
        for (var year = 2009; year <= new Date().getFullYear(); year++) {
            years.push([year, year]);
        }
        return years.reverse();
    },

    _getDocumentsFields: function(cfg) {
        return [
            {
                fieldLabel: 'Mês',
                xtype: 'combo',
                width: 200,
                split: true,
                hiddenName: 'mes',
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
            },
            {
                width: 200,
                allowBlank: false,
                fieldLabel: 'Ano',
                name: 'ano',
                xtype: 'combo',
                store:  this.getRangeOfYears()
            },
            {
                width: 200,
                allowBlank: true,
                fieldLabel: "Membro",
                name: "membro",
                xtype: "rest-autocompletefield",
                rest: "rh.employee.Restful",
                preFilter: [
                    {'property':  'ativo', 'value': true, 'stage': 1}
                ]
            }
        ]
    },

    _buildReport: function(file_type){

        values = this.getFormPanel().getForm().getValues()

	    engine.mq.Report.request({
	        report: '/to/mpe/expediente/exercicios_membros_detalhado_meses',
            el: this.getEl(),
	        waitMessage: 'Gerando relatório...',
	        // params: {
	        // },
            params: Ext.apply(
                values,
                {
                    outfile: 'relatorio_orgao_de_execucao' + new Date().format("d/m/Y"),
                    report_name: 'Relatório de exercícios em órgão de execução dos membros por mês'
                }
            ),
	    }, file_type);
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
	        	items: [

                {
                    xtype: 'fieldset',
                    width: 500,
	        		style: 'margin: 5px',
	        		align: 'center',
                    title: 'Relatório de exercícios em órgão de execução dos membros por mês',
                    items: 
                    [
                        this.getFormPanel(),
                        {
                            xtype: 'button',
                            iconCls: 'icon-siatu icon-siatu-move-down',
                            style: 'margin-top: 10px',
                            align: 'center',
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
			   title: 'Relatório de exercícios em órgão de execução dos membros por mês'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[ 
					this.getMain(),
				]
			},
		);
	
        rh.reports.ReportMemberActivitiesMonth.superclass.constructor.call(this, cfg);
	}
});