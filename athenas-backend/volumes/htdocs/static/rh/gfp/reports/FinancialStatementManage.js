/**
 *
 **/

Ext._define('rh.gfp.reports.FinancialStatementManage', {
	extend: 'toolkit.widget.TabPanel',

	_generateFichaFinanceira: function(){
			
        if(this.getEmployeeField().getValue() && this.getStartField().getValue()){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'RelatorioFichaFinanceira',
                    'generate_report'
                ),
                params: {
					ano_inicial: this.getStartField().getValue(),
					servidor_id: this.getEmployeeField().getComboField().getValue(),
					ano_final: this.getEndField().getValue() == "" ? this.getStartField().getValue() : this.getEndField().getValue()
                },
                success: function(request) {
					var obj = Ext.decode(request.responseText);
					Ext.Msg.show({
                        title: 'Solicitando Relatório',
                        msg: obj.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    })
                },
                failure: function() {
                    alert('Ocorreu um erro tentando gerar o relatorio.');
                },
                scope: this
            });
        }else Ext.Msg.show({
            msg: 'Selecione Tipo folha e Periodo',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

    getEmployeeField: function(){
		if(!this._employeefield)
			this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 400,
                comboListeners: {
                    scope: this,
                    changevalid: function(cmb, nv, ov, valid){
						if (valid) {
                            console.debug('CHANGE VALID('+valid+'): '+cmb.getValue());
                            var st = this.getPensionerField().getStore();
                            st.setBaseParam('employee', nv);
                            this.getPensionerField().clearValue();
                            st.load({});
                        }else{
                            console.debug('CHANGE VALID('+valid+'): '+cmb.getValue());
                            if(this._formPanel){
                                var st = this.getPensionerField().getStore();
                                st.removeAll();
                                this.getPensionerField().clearValue();
                            }

//                                     console.info(this._formPanel.getForm().findField("pensioner"));
                        }
                    }
				}
			});

		return this._employeefield;
	},

	getPensionerField: function(){
		if(!this._pensionerfield)
			this._pensionerfield = Ext._create('core.fields.ComboField', {
                name: 'pensioner',
                hiddenName: 'pensioner',
                rest: 'rh.pension.PensionerRestful',
                fieldLabel: 'Pensionista',
                width: 400,
                triggerAction: 'all',
                lazyRender: true,
                lazyInit: true
                // disabled: false
			});

		return this._pensionerfield;
	},

	getStartField: function(){
		if(!this._startfield)
			this._startfield = Ext._create('Ext.form.ComboBox', {
                name: 'start',
                hiddenName: 'start',
                fieldLabel: 'Inicio',
                width: 400,
                store: new Ext.data.JsonStore({
	                url: toolkit.util.Normalize.controller_action('GFPFinancialStatementReport', 'year'),
	                fields: ['year'],
	                autoLoad: true,
	                root: 'result',
	            }),
	            displayField: 'year',
	            valueField: 'year',
	            editable: false,
	            emptyText: 'Ano Inicio',
	            triggerAction: 'all',
	            mode: 'local',
			});

		return this._startfield;
	},

	getEndField: function(){
		if(!this._endfield)
			this._endfield = Ext._create('Ext.form.ComboBox', {
                name: 'end',
                hiddenName: 'end',
                fieldLabel: 'Fim',
                width: 400,
                store: new Ext.data.JsonStore({
	                url: toolkit.util.Normalize.controller_action('GFPFinancialStatementReport', 'year'),
	                fields: ['year'],
	                autoLoad: true,
	                root: 'result',
	            }),
	            displayField: 'year',
	            valueField: 'year',
	            editable: false,
	            emptyText: 'Ano Fim',
	            triggerAction: 'all',
	            mode: 'local',
			});

		return this._endfield;
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
	        		title: 'Impressão de Ficha Financeira',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        			this.getEmployeeField(),
	        			// this.getPensionerField(),
	        			this.getStartField(),
	        			this.getEndField(),
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Ficha Financeira',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this._generateFichaFinanceira,
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
			   title: 'Relatório -> Ficha Financeira'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					this.getMain(),
				]
			}
		);

		rh.gfp.reports.FinancialStatementManage.superclass.constructor.call(this, cfg);
	}
});