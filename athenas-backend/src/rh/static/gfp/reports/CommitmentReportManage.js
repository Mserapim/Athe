Ext._define('rh.gfp.reports.CommitmentReportManage', {
	extend: 'toolkit.widget.TabPanel',

	_commitmentReport: function(option,subtitle){
        var sheet = this.getSheetField().getValue();
		if (sheet) {
				Ext.Ajax.request({
					url: toolkit.util.Normalize.controller_action('GFPCommitmentReport', 'create_pdf'),
					params: {
						sheet: sheet,
						option:option,
						type:'commitment',
						report:"Empenhos",
						subtitle:subtitle
					},
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
			}
		else
			Ext.Msg.show({
				msg: 'Primeiro selecione uma Folha de Pagamento..',
				icon: Ext.Msg.ERROR,
				buttons: Ext.Msg.OK
			})
	
    },

	_lrfReport: function(){
        var sheet = this.getSheetField().getValue();
		if (sheet) {
				Ext.Ajax.request({
					url: toolkit.util.Normalize.controller_action('GFPCommitmentReport', 'create_pdf'),
					params: {
						sheet: sheet,
						type:'lrf',
						report:"LRF"
					},
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
			}
		else
			Ext.Msg.show({
				msg: 'Primeiro selecione uma Folha de Pagamento..',
				icon: Ext.Msg.ERROR,
				buttons: Ext.Msg.OK
			})
	
    },

    getSheetField: function(){
		if(!this._sheetfield)
			this._sheetfield = Ext._create('core.fields.AutocompleteField', {
                name: 'sheet',
                rest: 'rh.gfp.payroll.PayrollRestful',
                fieldLabel: 'Folha',
                width: 400,
			});

		return this._sheetfield;
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
	        		title: 'Relatório de folha para fins de empenhos e LRF',
	        		name: 'sheet_type',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        			this.getSheetField(),
						
						
	        		],
					buttons:[
						// {
						// 	xtype: 'button',
						// 	iconCls: 'icon-siatu icon-siatu-move-down',
						// 	style: 'margin-top: 10px',
						// 	text: 'Gerar Relatório de Empenhos', 
						// 	width: 100,
						// 	height: 25,
						// 	scope: this,
						// 	handler: this._commitmentReport,
						// },
						{
							text: 'Gerar Relatório de Empenhos',
							width: 100,
							style: 'margin-top: 10px',
							iconCls: 'icon-siatu icon-siatu-move-down',
							height: 25,
							scope: this,
							menu:{
								scope: this,
								items: [
									{
										text: 'Tudo ',
										type: 'button',
										scope: this,
										handler: function () {
											this._commitmentReport(0,"")
										}
									},
									{
										text: 'Relatório Plano Financeiro',
										type: 'button',
										scope: this,
										handler: function () {
											this._commitmentReport(2,'Plano Financeiro')
										}
									},
									{
										text: 'Relatório Plano Previdenciário ',
										type: 'button',
										scope: this,
										handler: function () {
											this._commitmentReport(1,'Plano Previdenciário')
										}
									},
									{
										text: 'Outros',
										type: 'button',
										scope: this,
										handler: function () {
											this._commitmentReport(99,'Outros')
										}
									},
								]
							}
						},
						{
							xtype: 'button',
							iconCls: 'icon-siatu icon-siatu-move-down',
							style: 'margin-top: 10px',
							text: 'Gerar Relatório LRF',
							width: 100,
							height: 25,
							scope: this,
							handler: this._lrfReport,
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
			   title: 'Relatório de Empenhos e LRF'
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

		rh.gfp.reports.CommitmentReportManage.superclass.constructor.call(this, cfg);
	}
});