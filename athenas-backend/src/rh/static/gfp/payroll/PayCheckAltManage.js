/**
 *
 **/

Ext._define('rh.gfp.payroll.PayCheckAltManage', {
	extend: 'toolkit.widget.TabPanel',

	getToolbar: function() {
		var t = new Ext.Toolbar({
			width: 500,
			height: 100,
			items: [
			{
				text: 'Teste'
			}
			]
		});

		return t;
	},

	getEntriesGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.payroll.EntriesGrid', {
				region: 'center',
				gridAutoLoad: false,
				title: 'Eventos',
				disabled: true,
				split: true,
				allEvent: this
				// payroll_event: 
			});

		return this._grid;
	},

	getPayrollStatusField: function(){
		if(!this._payrollsf)
			this._payrollsf = Ext._create('Ext.form.DisplayField', {
                value: ' ',
                hideLabel: true,
                name: 'payroll_status',
                height: 16,
                width: 18,
                style: 'margin: 6px 0 0 15px'
			});

		return this._payrollsf;
	},

	getPayrollField: function(){
		if(!this._payrollfield)
			this._payrollfield = Ext._create('core.fields.AutocompleteField', {
                name: 'payroll',
                rest: 'rh.gfp.payroll.PayrollRestful',
                hideLabel: true,
                tabIndex: 1,
                comboListeners: {
                    scope: this,
                    changevalid: function(cmb, nv, ov, valid){
                        console.debug('CHANGE VALID('+valid+'): '+cmb.getValue());
                        if(valid){
                        	this.setPayrollStatus(cmb.getStore().data.get(0).json);
                        	this.getEmployeeField().setDisabled(false);
                        	this.loadPayCheck();
                        }
                        else{
                        	payroll = null;

                        }
                    }
            	},
			});

		return this._payrollfield;
	},


	setEvent: function(create){

		if(create){
			this.getPayrollEventField().enable();
		}

		var qnt_field = form.findField('qnt');
        var qnt_max_field = form.findField('qnt_max');
        var pct_field = form.findField('pct');
        var parcela_field = form.findField('parcela');
        var prazo_field = form.findField('prazo');
        var valor_field = form.findField('valor');
        var valor_base_field = form.findField('valor_base');
        var patronal_field = form.findField('patronal');
        var base_previdencia_field = form.findField('base_previdencia');
        var info_field = form.findField('info');
        var reference_year_field = form.findField('reference_year');
        var reference_month_field = form.findField('reference_month');
        var choices_field = form.findField('oIds');

		if(disable){
			
			



		}
	},

	cancelAction: function(){
		this.disableAll();
	},

	clearAll: function(){
		var form = this.getEventGrid().getForm();
		this.getPayrollEventField().setValue();
		form.findField('qnt').setValue();
        form.findField('qnt_max').setValue();
        form.findField('pct').setValue();
        form.findField('parcela').setValue();
        form.findField('prazo').setValue();
        form.findField('valor').setValue();
        form.findField('valor_base').setValue();
        form.findField('patronal').setValue();
        form.findField('base_previdencia').setValue();
        form.findField('info').setValue("");
        form.findField('reference_year').setValue();
        form.findField('reference_month').setValue();
        form.findField('oIds').setValue();
	},

	disableAll: function(){
		this.clearAll();
		var form = this.getEventGrid().getForm();
		this.getPayrollEventField().setDisabled(true);
		form.findField('qnt').setDisabled(true);
        form.findField('qnt_max').setDisabled(true);
        form.findField('pct').setDisabled(true);
        form.findField('parcela').setDisabled(true);
        form.findField('prazo').setDisabled(true);
        form.findField('valor').setDisabled(true);
        form.findField('valor_base').setDisabled(true);
        form.findField('patronal').setDisabled(true);
        form.findField('base_previdencia').setDisabled(true);
        form.findField('info').setDisabled(true);
        form.findField('reference_year').setDisabled(true);
        form.findField('reference_month').setDisabled(true);
        form.findField('oIds').setDisabled(true);
        this.getCancelButton().setDisabled(true);
        this.getEntriesGrid().setDisabled(false);
	},

	setEventData: function(e){
		if(e !== null) this._event = e;
	},

	getEventData: function(){
		return this._event;
	},	

	getPayrollEventField: function(){
		if(!this._payrolleventfield)
			this._payrolleventfield = Ext._create('core.fields.AutocompleteField', {
                name: 'payroll_event',
                rest: 'rh.gfp.payroll.EventRestful',
                // hideLabel: true,
                fieldLabel: 'Evento',
                margins: '0 0 5 0',
                // width: 600,
                disabled: true,
                comboListeners: {
                    scope: this,
                    changevalid: function(cmb, nv, ov, valid){
                        console.debug('CHANGE VALID('+valid+'): '+cmb.getValue());
                        if(valid){
                            if(!this.getEventData() || this.getEventData().pk!=nv){
                                idx = cmb.getStore().findExact(cmb.valueField, nv);
                                this.setEventData(cmb.getStore().getAt(idx).data);
                                console.debug('LOAD FOLHA EVENTO FOR EVENTO '+this.getEventData().unicode);
                                this.clearAll();
                                this.infoEvento({});
                            }
                        }else{
                            this.setEventData(null);
                        }
                    },
                },
			});
	    
	    return this._payrolleventfield;               	
	},

	getEmployeeField: function(){
		if(!this._employeefield)
			this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                hideLabel: true,
                disabled: true,
                tabIndex: 2,
                comboListeners: {
                    scope: this,
                    changevalid: function(cmb, nv, ov, valid){
                        console.debug('CHANGE VALID('+valid+'): '+cmb.getValue());
                        if(valid){                                       	
                        	this.loadPayCheck();
                        }
                        else{
                        	payroll = null;

                        }
                    }
            	}
			});

		return this._employeefield;
	},

	setPayroll: function(payroll) {
		this.getPayrollField().setValue(payroll.pk);
	},

	setPayrollStatus: function(payroll) {
		this.getPayrollStatusField().addClass(payroll.icons[0].iconCls);
	},

	loadPayCheck: function() {

		this.employee = this.getEmployeeField().getValue();
		this.payroll = this.getPayrollField().getValue();

		if(this.employee && this.payroll){
			this.getEntriesGrid().enable();

        	this.getEntriesGrid().setParam('servidor', this.employee);
        	this.getEntriesGrid().setFilterProperty('servidor', this.employee, 0);

        	this.getEntriesGrid().setParam('folha', this.payroll);
        	this.getEntriesGrid().setFilterProperty('folha', this.payroll, 1);
		}
	},

	getCurrentPayroll: function(){
		Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                'GFPPayroll', 
                'working'
            ),
            method: 'POST',
            success: function(request) {   
                var code = Ext.decode(request.responseText);
                this.setPayroll(code.payroll);
            },
            scope: this
        });
	},

	markDirty: function(field){
        console.debug('MARKDIRTY '+ field.name);
        if(this.cfg.markIfDirty && field.isDirty()){
            field.getEl().setStyle('background-color','#ff7777');
        }else{
            field.getEl().setStyle('background-color','#d1d1d1');
        }
    },

	getEventGrid: function(){

		if(!this._eventGrid)
			this._eventGrid = Ext._create('Ext.form.FormPanel', {
			title: 'Dados do Evento',
			region: 'center',
			// disabled: true,
			items: [
			//Fieldset Evento
			{
				xtype: 'fieldset',
				width: 630,
				// title: 'Evento',
				style: 'margin: 5px 0 5px 5px; padding: 5px 5px 0 10px',
				items: [
	            	this.getPayrollEventField(),
	            	{
	            		layout: 'form',
	            		border: false,
	            		style: 'padding: 5px 0 0 0',
	            		items: [
	            			{
		                        xtype: 'combo',
		                        width: 500,
		                        typeAhead: true,
		                        triggerAction: 'all',
		                        lazyRender:true,
		                        mode: 'local',
		                        store: new Ext.data.ArrayStore({
		                            id: 0,
		                            fields: [
		                                'oId',
		                                'displayText'
		                            ],
		                            data: []
		                        }),
		                        valueField: 'oId',
		                        displayField: 'displayText',
		                        hiddenName: 'oIds',
		                        disabled: true,
		                        editable: false,
		                        fieldLabel: 'Opções',
		                        listeners: {
		                            scope: this,
		                            // change: this.changeValue,
		                            // valid: this.markDirty,
		                        },                                
		                    },
	            		]
	            	}
	            	
	            ]
	        },
	        //Fieldset Qtd, Perc., Prazo, Valor, Valor Base, Patronal, Base Prev.
	        {
	        	xtype: 'fieldset',
	        	width: 630,
	        	style: 'margin: 0 0 0 5px; padding: 5px 5px 0 10px',
	        	items:[
	        	{
	        		border: false,
	        		layout: 'hbox',
	        		items:[
	            	{
						layout: 'form',
						labelAlign: 'top',
						margins: '0 5 0 0',
						border: false,
						items: [
						{
							xtype: 'numberfield',
							name: 'qnt',
							fieldLabel: 'Quantidade',
							width: 95,
							disabled: true
						}
						]
					},
					{
						layout: 'form',
						labelAlign: 'top',
						margins: '0 5 0 0',
						border: false,
						items: [
						{
							xtype: 'numberfield',
							name: 'qnt_max',
							fieldLabel: 'Qtd. Base',
							width: 95,
							disabled: true
						}
						]
					},
					{
						layout: 'form',
						labelAlign: 'top',
						margins: '0 5 0 0',
						border: false,
						items: [
						{
							xtype: 'numberfield',
							name: 'pct',
							fieldLabel: 'Percentual',
							width: 95,
	                    	disabled: true
						},
						]
					},
					{
						layout: 'form',
						labelAlign: 'top',
						margins: '0 5 0 0',
						border: false,
						items: [
						{
							xtype: 'numberfield',
							name: 'prazo',
							fieldLabel: 'Prazo',
							width: 95,
	                    	disabled: true
						},
						]
					},
					{
						layout: 'form',
						labelAlign: 'top',
						margins: '0 5 0 0',
						border: false,
						items: [
						{
							xtype: 'numberfield',
							name: 'parcela',
							fieldLabel: 'Parcela',
							width: 95,
	                    	disabled: true
						},
						]
					},
					{
						layout: 'form',
						labelAlign: 'top',
						margins: '0 5 0 0',
						border: false,
						items: [
						{
							xtype: 'numberfield',
							name: 'valor',
							fieldLabel: 'Valor',
							width: 95,
							disabled: true
						}
						]
					},
					]
				},
				{
	        		border: false,
	        		layout: 'hbox',
	        		items:[
					{
						layout: 'form',
						labelAlign: 'top',
						margins: '0 5 0 0',
						border: false,
						items: [
						{
							xtype: 'numberfield',
							name: 'valor_base',
							fieldLabel: 'Valor Base',
							width: 95,
	                    	disabled: true
						},
						]
					},
					{
						layout: 'form',
						labelAlign: 'top',
						margins: '0 5 0 0',
						border: false,
						items: [
						{
							xtype: 'numberfield',
							name: 'patronal',
							fieldLabel: 'Patronal',
							width: 95,
	                    	disabled: true
						},
						]
					},
					{
						layout: 'form',
						labelAlign: 'top',
						margins: '0 5 0 0',
						border: false,
						items: [
						{
							xtype: 'numberfield',
							name: 'base_previdencia',
							fieldLabel: 'Base Prev.',
							width: 95,
	                    	disabled: true
						},
						]
					},
					{
                        layout: 'form',
                        labelAlign: 'top',
                        border: false,
                        items: {
                            width: 198,
                            fieldLabel: 'Mês/Ref.',
                            // style: 'margin: 0 5px 0 0',
                            name: 'reference_month',
                            tabIndex: 12,
                            // value: Ext.isNumber(this.cfg.reference_month)? this.cfg.reference_month: this.cfg.folha.periodo_mes,
                            disabled: true,
                            // listeners: {
                            //     scope: this,
                            //     valid: this.markDirty,
                            // },
                            xtype: 'combo',
                            hiddenName: 'reference_month',
                            store: [
                                [ 1, 'JANEIRO'],
                                [ 2, 'FEVEREIRO'],
                                [ 3, 'MARÇO'],
                                [ 4, 'ABRIL'],
                                [ 5, 'MAIO'],
                                [ 6, 'JUNHO'],
                                [ 7, 'JULHO'],
                                [ 8, 'AGOSTO'],
                                [ 9, 'SETEMBRO'],
                                [10, 'OUTUBRO'],
                                [11, 'NOVEMBRO'],
                                [12, 'DEZEMBRO'],
                            ],
                            triggerAction: 'all'
                            }
                    },
                    {
                        layout: 'form',
                        labelAlign: 'top',
                        border: false,
                        items: {
                            width: 95,
                            fieldLabel: 'Ano/Ref.',
                            style: 'margin: 0 0 0 5px',
                            xtype: 'numberfield',
                            name: 'reference_year',
                            tabIndex: 13,
                            // value: Ext.isNumber(this.cfg.reference_year)? this.cfg.reference_year: this.cfg.folha.periodo_ano,
                            disabled: true,
                            // listeners: {
                            //     scope: this,
                            //     valid: this.markDirty,
                            // },
                        }
                    }
					]
				},
				//Fieldset Informações do Evento
				{
					layout: 'hbox',
					border: false,
					items: [
					{	
						layout: 'form',
						border: false,
						labelAlign: 'top',
						items: [
						{
							xtype: 'textfield',
		                	name: 'info',
		                	width: 400,
		                	disabled: true,
		                	fieldLabel: 'Informações'
		                }
						]
		            },
		            {
			        	// xtype: 'fieldset',
						width: 630,
						layout: 'column',
						style: 'padding: 18px 0 0 10px', 
						// title: 'Ações',
						border: false,
						items: [
			            this.getSaveButton(),
			            this.getCancelButton()
			            ]
			        }
					]
				}
	        	]	
	        },

			]
		});

		return this._eventGrid;
	},

	getSaveButton: function() {
	    if(!this._showSaveButton)
	        this._showSaveButton = new Ext.Button({
	            style: 'margin: 0 5px 0 0',
                text: 'Salvar',
                iconCls: 'icon-core icon-core-success',
                scope: this,
                width: 95,
                disabled: true,
	            handler: this.saveAction
	        });

	    return this._showSaveButton;
	},

    getCancelButton: function() {
	    if(!this._showCancelButton)
	        this._showCancelButton = new Ext.Button({
	            text: 'Cancelar',
	            iconCls: 'icon-core icon-core-delete',
	            style: 'margin: 0 5px 0 5px',
	            width: 95,
			    disabled: true,
	            scope: this,
	            handler: this.cancelAction
	        });

	    return this._showCancelButton;
	},

	infoEvento: function(params){
        var form = this.getEventGrid().getForm();
        var lm = new Ext.LoadMask(this.getEl(), {'msg': 'Processando...'});
        

        // console.debug('Executing INFO EVENTO...');
        // console.debug(this.cfg);
        if(this.getEventData()){
            if(this.getEventData().automatico === true){
                lm.show();                
                Ext.applyIf(params, {servidor: this.cfg.servidor.pk, folha: this.cfg.folha.pk, evento: this.getEventData().pk});
                if(this.cfg.folhaevento){
                    Ext.applyIf(params, {folhaevento: this.cfg.folhaevento})
                }
                qnt_field = this.formPanel.getForm().findField("qnt");
                if( [3, 4, 5].indexOf(this.getEventData().tipo_calculo) >= 0 && Ext.isNumber(qnt_field.getValue())){
                    Ext.applyIf(params, {qnt: qnt_field.getValue()});
                }
                pct_field = this.formPanel.getForm().findField("pct");
                if([1, 4, 5].indexOf(this.getEventData().tipo_calculo) >= 0 && Ext.isNumber(pct_field.getValue())){
                    Ext.applyIf(params, {pct: pct_field.getValue()});
                }
                info_field = this.formPanel.getForm().findField("info");
                choices_field = this.formPanel.getForm().findField("oIds");
                if(choices_field.getValue())
                    Ext.applyIf(params, {oIds: choices_field.getValue()});
                    
                Ext.applyIf(params, {info: info_field.getValue()});
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPLancador', 'info_evento'),
                    params: params,
                    scope: this,
                    success: function(request) {
                        // var cfg = {};
                        var data_folhaevento = Ext.decode(request.responseText);
                        Ext.apply(this.cfg, data_folhaevento);
                        this.applyInformation(this.cfg);
                        lm.hide();
                    },
                    failure: function(request){
                        lm.hide();                                
                        alert('Erro ao processar requisição! Informe ao departamento de TI.');
                    }
                })                                        
            }else{
                this.applyInformation(this.cfg);
            }
        }else{
            console.error('Evento não definido!');
        }
    },

	getMain: function(){
		if(!this._panel)
		this._panel = new Ext.Panel({
		    layout: 'border',
		    region: 'center',
		    height: 650,
		    split: true,
		    items: [
		    this.getToolbar(),
			{
		        region: 'north',
		        layout: 'border',
		        height: 440,
		        items:[
		        //Periodo, Dados do Eventos
		        {
		        	region: 'west',
		        	layout: 'border',
		        	width: 640,
		        	border: false,
		        	items: 
		        	[
		        	// Período e Tipo de Folha
		        	{
		        		title: 'Período',
		        		layout: 'border',
		        		region: 'north',
		        		border: true,
		        		height: 165,
		        		items: [
		        		//Fieldset Periodo
		        		{
		        			region: 'center',
		        			width: 370,
		        			layout: 'hbox',
		        			border: false,
		        			items: [
		        			//Fieldset Mes
		        			{
		        				xtype: 'fieldset',
		        				title: 'Folha',
		        				width: 550,
		        				margins: '5 5 0 5',
		        				items: [
		        					this.getPayrollField()
		        				]
		        			},	        			
		        			//Fieldset Tipo de Folha
		        			{
		        				xtype: 'fieldset',
		        				title: 'Status',
		        				width: 70,
		        				height: 63,
		        				margins: '5 5 0 5',
		        				items: [
			                        this.getPayrollStatusField(),
		        				]
		        			}
		        			]
	        			},
	        			//Fieldset Informações da Folha e Servidor
	        			{
	        				region: 'south',
	        				width: 370,
	        				border: false,
	        				items: 
	        				[
	        				//Fieldset Servidor
	        				{
		        				xtype: 'fieldset',
		        				title: 'Servidor',
		        				width: 630,
		        				style: 'margin: 0 0 5px 5px',
		        				items: [
		        					this.getEmployeeField()
		        				]
		        			},
		        			]
	        			}
		        		]
		        	},
		        	//Dados do Evento
		        	this.getEventGrid(),
		        	]
		        },
		        // 'Informações do Contra-Cheque',
		        {
			        region: 'center',
			        layout: 'border',
			        items: [
			        {
			        	title: 'Informações do Contra-Cheque',
			        	region: 'center',
			        	border: false,
			        	items: [
			        	//Fieldset Matricula/Servidor
			        	{
			        		xtype: 'fieldset',
			        		title: 'Matricula/Servidor',
			        		name: 'fieldServidor',
			        		width: "97%",
			        		style: 'margin: 5px',
			        		items:[
			        		{
			        			hideLabel: true,
			        			xtype: 'displayfield',
			        			value: '124414 - Jan Tarik Martins Nazorek'
			        		}
			        		]
			        	},
			        	//Fielset Cargos
			        	{
			        		xtype: 'fieldset',
			        		title: 'Cargos',
			        		name: 'fieldServidor',
			        		width: "97%",
			        		style: 'margin: 5px',
			        		labelWidth: 65,
			        		items:[
			        		{
			        			fieldLabel: 'Efetivo',
			        			xtype: 'displayfield',
			        			value: 'Técnico Ministerial Especializado - Informática',
			        		},
			        		{
			        			fieldLabel: 'Comissão',
			        			xtype: 'displayfield',
			        			value: '-'
			        		},
			        		{
			        			fieldLabel: 'Eletivo',
			        			xtype: 'displayfield',
			        			value: '-'
			        		}
			        		]
			        	},
			        	//Fieldset Dados Bancários
			        	{
			        		xtype: 'fieldset',
			        		title: 'Dados Bancários',
			        		name: 'fieldServidor',
			        		width: "97%",
			        		style: 'margin: 5px',
			        		items:[
			        		{
			        			hideLabel: true,
			        			xtype: 'displayfield',
			        			value: '-'
			        		}
			        		]
			        	},
			        	//Fieldset Margens
			        	{
			        		xtype: 'fieldset',
			        		title: 'Margens Consignáveis',
			        		name: 'fieldServidor',
			        		width: "97%",
			        		style: 'margin: 5px',
			        		layout: 'hbox',
			        		items:[
			        		{
			        			layout: 'form',
			        			labelWidth: 40,
			        			margins: '0 10 0 0',
			        			border: false,
			        			items: 
			        			[
			        			{
			        				fieldLabel: 'Total',
			        				xtype: 'displayfield',
			        				value: 'R$ 1000,00'
			        			}
			        			]
			        		},
			        		{
			        			layout: 'form',
			        			labelWidth: 65,
			        			border: false,
			        			items:
			        			[
			        			{
			        				fieldLabel: 'Disponível',
			        				xtype: 'displayfield',
			        				value: 'R$ 1000,00'
			        			}
			        			]
			        		}
			        		]
			        	}
			        	]
			        }
			        ],
			        bodyStyle: {padding: '5px'},			        
	            }
		        
		        ]
            },
            //Eventos Grid
            this.getEntriesGrid()
		    ]	
		});

		return this._panel;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Lançamentos'
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

		this.getCurrentPayroll();

		rh.gfp.payroll.PayCheckAltManage.superclass.constructor.call(this, cfg);
	}
});
