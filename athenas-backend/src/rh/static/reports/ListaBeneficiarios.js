Ext._define('rh.reports.ListaBeneficiarios', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(file_type){

        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                'ListaBeneficiariosRelatorio',
                'generate_report'
            ),
            params: {
                ativo: this.getAtivo().getValue() == "" ? null : this.getAtivo().getValue(),
                cargo: this.getJobPosition().getValue() == "" ? null : this.getJobPosition().getValue(),
                servidor: this.getEmployeeField().getValue() == "" ? null : this.getEmployeeField().getValue(),
                tipo_arquivo: file_type,
                paridade_salarial: this.getParidade().getValue() == "" ? null : this.getParidade().getValue(),
                beneficio_integral: this.getIntegral().getValue() == "" ? null : this.getIntegral().getValue(),
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
    },

    getEmployeeField: function(){
		if(!this._employeefield)
			this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 350,
                preFilter: [
                    {property: 'type_by_possession__in', value: ['SAP','MAP','MAP2', 'APO', 'BFP'], stage: 1}
                ],
                gridConfig: {
                    configOrderToolBar: ['search', '->'],
                    columnAction: false,
                }
			});

		return this._employeefield;
	},

	getJobPosition: function(){
		if(!this._jobposition)
			this._jobposition = Ext._create('core.fields.AutocompleteField', {
                name: 'jobposition',
                rest: 'rh.jobposition.Restful',
                fieldLabel: 'Cargo',
                width: 350
			});

		return this._jobposition;
	},

	getAtivo: function(){
        if(!this._ativo){
            this._ativo = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Ativo',
                hiddenName: 'ativo',
                ativo: 'ativo',
                width: 350,
                triggerAction: 'all',
                store: [
                    ["SIM", 'SIM'],
                    ["NAO", 'NÃO']
                ],
                value:"SIM",
            });
        }

        return this._ativo;
    },


    getParidade: function(){
        if(!this._paridade){
            this._paridade = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Paridade Salarial',
                hiddenName: 'paridade',
                width: 350,
                triggerAction: 'all',
                store: [
                    ["SIM", 'SIM'],
                    ["NAO", 'NÃO']
                ],
            });
        }

        return this._paridade;
    },

    getIntegral: function(){
        if(!this._integral){
            this._integral = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Beneficio Integral',
                hiddenName: 'integral',
                width: 350,
                triggerAction: 'all',
                store: [
                    ["SIM", 'SIM'],
                    ["NAO", 'NÃO']
                ],
            });
        }

        return this._integral;
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
	        		title: 'Impressão da Listagem de Beneficiarios',
	        		name: 'fieldServidor',
	        		width: 500,
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        			this.getEmployeeField(),
	        			this.getJobPosition(),
	        			this.getAtivo(),
	        			this.getParidade(),
	        			this.getIntegral(),
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
                    	value: '* Deixe os campos em branco para selecionar Todos',
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
			   title: 'Relatório -> Listagem de Beneficiarios'
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


		// rh.gfp.reports.PayCheckManage.superclass.constructor.call(this, cfg);
		rh.reports.ListaBeneficiarios.superclass.constructor.call(this, cfg);
	}
});