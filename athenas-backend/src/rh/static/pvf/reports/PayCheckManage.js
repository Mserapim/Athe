/**
 *
 **/

 Ext._define('rh.pvf.reports.PayCheckManage', {
	extend: 'toolkit.widget.TabPanel',

	_generatePaycheck: function(){
        if(this.getPayrollTypeField().getValue() && this.getMonthField().getValue() && this.getYearField().getValue()){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'PVFPayCheckReport',
                    'paycheck_list'
                ),
                params: {
                    type: this.getPayrollTypeField().getValue(),
                    month: this.getMonthField().getValue(),
                    year: this.getYearField().getValue()
                },
                success: function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(obj.success)
                        this._buildPaycheck(obj.list_paycheck);
                    else
                        Ext.Msg.show({
                            title: 'Holerite',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                },
                failure: function() {
                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                    });
                },
                scope: this
            });
        }else Ext.Msg.show({
            msg: 'Selecione Tipo folha, Mês e Ano.',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

	_buildPaycheck: function(paycheck){

        var type = this.getPayrollTypeField().lastSelectionText
        var month = this.getMonthField().getValue()
        var year = this.getYearField().getValue()
        engine.mq.Report.request({
            report: '/to/mpe/gfp/paycheck_by_id',
            waitMessage: 'Gerando relatório...',
            params: {

                outfile: 'contracheque'+'-' + type + '-' + month + '-' + year,
                report_name: 'Contra-cheque'  + ' - ' + type + ' - ' + month + ' - ' + year,
                contracheque: paycheck,
                admin: 1
            }

        });
    },

    getPayrollTypeField: function() {
        if (!this._typefield) {
            this._typefield = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Tipo folha',
                hiddenName: "type",
                hidden: true,
                width: 400,
                value: 999999,
                displayField: 'description',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                      url: core.callAction('PVFPayCheckReport', 'get_payroll_types')
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
                listeners: {
                    load:{
                        scope: this,
                        fn: function(field, record) {
                            this.getTypesDisplay(this)
                        }                  
                    },
                },
                autoLoad: false
            });
        }
        return this._typefield;
    },

    getMonthField: function() {
        if (!this._monthfield) {
            this._monthfield = Ext._create('core.fields.ComboField', {
                fieldLabel: "Mês",
                hiddenName: "month",
                // value:new Date().getMonth()+1,
                width: 400,
                store:[
                   [1,'JANEIRO'],
                   [2,'FEVEREIRO'],
                   [3,'MARÇO'],
                   [4,'ABRIL'],
                   [5,'MAIO'],
                   [6,'JUNHO'],
                   [7,'JULHO'],
                   [8,'AGOSTO'],
                   [9,'SETEMBRO'],
                   [10,'OUTUBRO'],
                   [11,'NOVEMBRO'],
                   [12,'DEZEMBRO'],
                ],
                listeners: {
                    select: {
                        scope: this,
                        fn: function(field, record) {
                            this.getTypesDisplay(this)
                        }                  
                    },
                    change: {
                        scope: this,
                        fn: function(field, record) {
                            this.getTypesDisplay(this)
                        }                  
                    },
                },

                autoLoad: true
            });
        }

        return this._monthfield;
    },

    getYearField: function() {
        if (!this._yearfield) {
            this._yearfield = Ext._create('core.fields.ComboField', {
                fieldLabel: "Ano",
                hiddenName: "year",
                width: 400,
                // value:new Date().getFullYear(),
                displayField: 'description',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                      url: core.callAction('PVFPayCheckReport', 'get_year')
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
                listeners: {
                    select: {
                        scope: this,
                        fn: function(field, record) {
                            this.getTypesDisplay(this);
                        }                  
                    },
                    change: {
                        scope: this,
                        fn: function(field, record) {
                            this.getTypesDisplay(this);
                        }                  
                    },                        
                },
                autoLoad: true
            });
        }

        return this._yearfield;
    },

    getTypesDisplay: function(scope){
        if (this.getYearField().getValue() != '' && this.getMonthField().getValue() != '' ) {
            
            Ext.getCmp('submit').disable();

            this.getPayrollTypeField().getStore().removeAll();
            scope.getPayrollTypeField().getStore().setBaseParam('month', scope.getMonthField().getValue())
            scope.getPayrollTypeField().getStore().setBaseParam('year', scope.getYearField().getValue())

            if (scope.getPayrollTypeField().getStore().reader.jsonData.count < 1 ) {
                scope.getPayrollTypeField().setValue(999998);
                scope.getPayrollTypeField().show();
            
            } else{
                scope.getPayrollTypeField().setValue(999999);
                scope.getPayrollTypeField().enable();
                scope.getPayrollTypeField().show();
                Ext.getCmp('submit').enable();

            }
        }
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
	        		title: 'Impressão do Holerite',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
                        this.getMonthField(),
                        this.getYearField(),
                        this.getPayrollTypeField(),
                    {
                        xtype: 'button',
                        id: 'submit',
                        disabled:true,
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Holerite',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this._generatePaycheck,
                    }
	        		]
	        	},
                {
                    fieldLabel: 'Info',
                    xtype: 'displayfield',
                    name: 'info',
                    labelStyle: 'font-weight:bold',
                    value: '<htm><p style="margin-top:30px;font-size:18px;font-weight:bold">Informamos que a partir de 2023 o holerite <br/> poderá acessado somente a partir da tela inicial. </p></html>'
	        	},
                {
                    fieldLabel: 'Info',
                    xtype: 'displayfield',
                    name: 'info',
                    labelStyle: 'font-weight:bold',
                    value: '<html> <img style="margin-top:10px;" width=800px src="static/rh/images/image-report-paycheck.png"/><html>'
	        	}              
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
			   title: 'Relatório -> Holerite'
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

		rh.pvf.reports.PayCheckManage.superclass.constructor.call(this, cfg);
	}
});