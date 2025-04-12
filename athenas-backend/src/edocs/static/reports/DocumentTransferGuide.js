/**
 *
 **/

Ext._define('edocs.reports.DocumentTransferGuide', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(type){
		data_inicial = this.getDataInicial().getValue();
		data_final = this.getDataFinal().getValue();
		servidor = this.getEmployee().getValue();
        unidade_origem = this.getUnidadeOrigem().getValue();

		if(data_final == "" || data_inicial == "" || unidade_origem == ""){
			Ext.Msg.show({
                title: 'Mensagem',
                msg: 'Todos os campos são de preenchimento obrigatório!',
                icon: Ext.Msg.WARNING,
                buttons: Ext.Msg.OK
            });
		} else {
	        engine.mq.Report.request({
	            report: '/to/mpe/protocolo/guia_transferencia_documentos',
	            waitMessage: 'Gerando relatório...',
	            params: {
	                outfile: 'guia_transferencia_documentos',
	                report_name: 'Guia de Transferência de Documentos',
	                data_inicial: Ext.util.Format.date(data_inicial, 'Y-m-d'),
	                data_final: Ext.util.Format.date(data_final, 'Y-m-d'),
	                servidor: servidor,
	                unidade_origem: unidade_origem
	            }
	        }, type);
	    }
    },

	getMain: function(cfg){
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
	        		title: 'Guia de Transferência de Documentos',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
					this.getDataInicial(),
					this.getDataFinal(),
	        		this.getUnidadeOrigem(cfg),
	        		this.getEmployee(cfg),
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
                    }
	        		]
	        	},
        		]
        	}
    		]
	    });

		return this._panel;
	},

    getUnidadeOrigem: function(cfg){
        if(!this._unidadeorigem)
            this._unidadeorigem = Ext._create('core.fields.AutocompleteField', {
                name: 'unidade_origem',
                rest: 'rh.generalorgan.Restful',
                fieldLabel: 'Unidade de Origem',
                width: 350,
                preFilter: [
                	{property: 'pk__in', value: cfg.work_locations, stage: 10},
                ]
            });

        return this._unidadeorigem;
    },

    getEmployee: function(cfg){
        if(!this._employee)
            this._employee = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: "rh.employee.Restful",
                fieldLabel: 'Servidor',
                width: 350,
                value: cfg.employee,
                hidden: true
            });

        return this._employee;
    },

    getDataInicial: function() {
        if (!this._dataincial)
            this._dataincial = Ext._create('Ext.form.DateField', {
                name: 'data_inicial',
                fieldLabel: "Data Inicial",
                hidden: false,
                width: 350,
            });
        return this._dataincial;
    },

    getDataFinal: function() {
        if (!this._datacriacaofim)
            this._datacriacaofim = Ext._create('Ext.form.DateField', {
                name: 'data_final',
                fieldLabel: "Data Final",
                hidden: false,
                width: 350,
            });
        return this._datacriacaofim;
    },


	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Relatório -> Guia de Transferência de Documentos'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[ 
					this.getMain(cfg),
				]
			}
		);

		// this.getCurrentPayroll();

		edocs.reports.DocumentTransferGuide.superclass.constructor.call(this, cfg);
	}
});