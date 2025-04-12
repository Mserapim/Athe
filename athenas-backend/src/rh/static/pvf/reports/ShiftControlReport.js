/*****************************************************************************
*                                                                            *
*                          Escala de plantões                          *
*                                                                            *
*****************************************************************************/
Ext._define('rh.pvf.reports.ShiftControlReport', {
	extend: 'toolkit.widget.TabPanel',

    BACKGROUND_COLOR: '#005a7d',
    CARD_HEIGHT: 200,
    CARD_WIDTH: 550,
    REGION: 'center',
    GAP: 50,
    LEFT_PADDING: 375,
    BOTTOM_PADDING: 100,

    REPORT_CLASS: 'ShiftControlReport',

    PDF_FUNCTION: 'generate_shift_manager_pdf',
    XLS_FUNCTION: null,
    CSV_FUNCTION: null,

    _getDefaults: function () {
        return {
            flex: 1,
            height: this.CARD_HEIGHT,
            width: this.CARD_WIDTH,
            baseCls: 'x-river-panel',
            align: this.REGION,
        };
    },

	_generateReport: function(function_name){
        
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                this.REPORT_CLASS,
                function_name
            ),
            params: {

                competence: this.getCompetenceField().getValue(),
                workplace: this.getWorkPlaceField().getValue(),
                employee: this.getEmployeeField().getValue()
            },
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                if (obj.success){
                    Ext.Msg.show({
                        title: 'Solicitando Relatório',
                        msg: obj.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    if (obj.download){
                        var RemoteObserver = core.RemoteObserver;
                        var cb = RemoteObserver.on('base-report', {
                            scope: this,
                            fn: function (data) {
                                console.log(data)
                                setTimeout(
                                    function() {
                                        toolkit.util.downloadFile({
                                            url: data.path,
                                            filename: data.filename,
                                            approach: 'download',
                                        });;
                                        RemoteObserver.un('base-report', {scope: this})
                                    
                                    },
                                    1000
                                );
                            
                            }
                        });

                        setTimeout( function() {
                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    this.REPORT_CLASS,
                                    'marker'
                                ),
                                params: {
                                    uuid: obj.uuid
                                },
                                success: function() {},
                                failure: function() {},
                            });
                        },
                        2000);


                    }
                }else{
                    Ext.Msg.show({
                        title: 'Não Foi possível gerar o relatório!',
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }     
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
    },

    getCompetenceField: function(config){
        date_current = new Date()
        if(!this._competenceField)
            this._competenceField = Ext._create('Ext.form.TextField', {
                name: 'competence',
                fieldLabel: 'Competência (mm/aaaa)',
                width: 400,
                value: date_current.getMonth() + 1 +'/'+date_current.getFullYear()
            }, config);

        return this._competenceField;
    },

    getWorkPlaceField: function(config){
        if(!this._workplaceField)
            this._workplaceField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Lotação",
                width: 400,
                name: "workplace",
                emptyText: 'Escolha uma lotação',
                rest: 'rh.workplace.Restful',
                gridConfig: {
                    configOrderToolBar: ['search', '->'],
                    hideColumns: [],
                    columnAction: false,
                },
                preFilter: [
                    {'property': 'gestor_plantao_dti', 'value': true, 'stage': 1},
                    {'property': 'gestor_plantao_final_semana', 'value': true, 'stage': 1},
                    {'property': 'gestor_plantao_recesso', 'value': true, 'stage': 1},
                    {'property': 'gestor_plantao_eleitoral', 'value': true, 'stage': 1},
                    {'property': 'gestor_plantao_pgj', 'value': true, 'stage': 1}

                ]
            }, config);

        return this._workplaceField;
    },

    getEmployeeField: function(config){
        if(!this._employeeField)
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Servidor",
                width: 400,
                name: "employee",
                rest: 'rh.employee.Restful',
                gridConfig: {
                    configOrderToolBar: ['search', '->'],
                    hideColumns: ['departure_unicode', 'elective_unicode', 'pk',  'ativo', 'user', 'tipo', 'pessoa_fisica',
                    'email', 'vpi', 'data_referencia_ferias', 'chefe_imediato', 'chefe_imediato_unicode', 'effective_unicode',
                    'data_exercicio','data_posse', 'data_desligamento', 'created_at', 'modified_at', 'created_by_unicode',
                    'modified_by_unicode','type_by_possession_display', 'event_esocial','commission_unicode','icons'],
                    columnAction: false,
                }
            }, config);

        return this._employeeField;
    },

	getMain: function(cfg){
		if(!this._panel)
		this._panel = new Ext.Panel({
            region: 'south',
		    height: 900,
            bodyStyle: {
                'background-color': `${this.BACKGROUND_COLOR}`,
            },           
            layout: {
                type: 'hbox',
                padding: `${this.GAP} ${this.GAP} ${this.BOTTOM_PADDING} ${this.LEFT_PADDING}`,
            },
            defaults: this._getDefaults(),
		    autoEl: {tag: 'center'},
		    items: [
	        {
	        	region: 'center',
                title: 'Escala de Plantão Servidores',
                bwrapStyle: [
                    'border-radius: 0px 0 8px 8px;',
                    'background-color: #005a7c;',
                    'font-size: 14px;',
                    'font-weight: bold;',
                    'cursor: default;',
                    'user-select: none;',
                ].join(''),
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		name: 'fieldServidor',
	        		align: 'center',
	        		items:[
                        this.getCompetenceField(),
                        this.getWorkPlaceField(),
                        this.getEmployeeField(),
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
                                        handler:function() { 
                                            this._generateReport(this.PDF_FUNCTION)
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
			   title: 'Escala de Plantão Servidores'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'fit',
				items:[ 
					this.getMain(cfg),
				]
			}
		);

		rh.pvf.reports.ShiftControlReport.superclass.constructor.call(this, cfg);
	}
});