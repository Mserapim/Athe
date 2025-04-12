Ext._define('ceaf.reports.Capacitation', {
	extend: 'toolkit.widget.TabPanel',

    BACKGROUND_COLOR: '#005a7d',
    CARD_HEIGHT: 320,
    CARD_WIDTH: 550,
    REGION: 'center',
    GAP: 50,
    LEFT_PADDING: 375,
    BOTTOM_PADDING: 100,

    PDF_FUNCTION: 'generate_capacitation_pdf',
    XLS_FUNCTION: 'generate_capacitation_xls',

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
                'CapacitationPDF',
                function_name
            ),
            params: {
                end_matricula: this.getEndMatriculaField().getValue(),
                start_matricula: this.getStartMatriculaField().getValue(),
                type_by_possession: this.getTypeByPossessionField().getValue(),
                capacitation: this.getCapacitationField().getValue(),
                end_competence: this.getEndCompetenceField().getValue(),
                start_competence: this.getStartCompetenceField().getValue(),
                participant_id: this.getNameField().getValue(),
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
                                        setTimeout( function() {
                                            Ext.Ajax.request({
                                                url: toolkit.util.Normalize.controller_action(
                                                    'CapacitationPDF',
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
                                    
                                    },
                                    1000
                                );
                            
                            }
                        });
                    }
                }else{
                    Ext.Msg.show({
                        title: 'Error',
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

    getStartMatriculaField: function(config){
        if(!this._start_matriculaField)
            this._start_matriculaField = Ext._create('Ext.form.NumberField', {
                name: 'start_matricula',
                fieldLabel: 'Matrícula Inicial',
                width: 400,
            }, config);

        return this._start_matriculaField;
    },

    getEndMatriculaField: function(config){
        if(!this._end_matriculaField)
            this._end_matriculaField = Ext._create('Ext.form.NumberField', {
                name: 'end_matricula',
                fieldLabel: 'Matrícula Final',
                width: 400,
            }, config);

        return this._end_matriculaField;
    },

    getNameField: function(config){
        if(!this._nameField)
            this._nameField = Ext._create('core.fields.AutocompleteField', {
                name: 'name',
                fieldLabel: 'Nome',
                rest: 'ceaf.capacitation.participants.Restful',
                width: 400,
            }, config);

        return this._nameField;
    },

    getTypeByPossessionField: function (cfg) {
        if (!this._typeByPossession) {
            cfg = cfg || {};
            Ext.applyIf(cfg, {
                fieldLabel: 'Tipo de Servidor',
                hiddenName: 'type_by_possession',
                name: 'type_by_possession',
                choiceId: 'rh.CLASSIF_EMPLOYEE_BY_POSSESSION',
                width: 400,
                valueField: 'cvalue',
            });
            this._typeByPossession = Ext._create('standard.fields.ChoiceField', cfg);
        }
        return this._typeByPossession;
    },

    getCapacitationField: function (config) {
        if (!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Capacitação',
                name: 'capacitation',
                rest: 'ceaf.capacitation.Restful',
                allowBlank: true,
                lazyRender: true,
                lazyInit: true,
            });
        }
        
        return this._employeeField;
    },

    getStartCompetenceField: function(config){
        if(!this._start_competenceField)
            this._start_competenceField = Ext._create('Ext.form.TextField', {
                name: 'start_competence',
                fieldLabel: 'Competência Inicial (mm/aaaa)',
                width: 400,
            }, config);

        return this._start_competenceField;
    },


    getEndCompetenceField: function(config){
        if(!this._end_competenceField)
            this._end_competenceField = Ext._create('Ext.form.TextField', {
                name: 'end_competence',
                fieldLabel: 'Competência Final (mm/aaaa)',
                width: 400,
            }, config);

        return this._end_competenceField;
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
                title: 'Relatório Sintetizado de Capacitações',
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
                        this.getStartMatriculaField(),
                        this.getEndMatriculaField(),
                        this.getTypeByPossessionField(),
                        this.getCapacitationField(),
                        this.getStartCompetenceField(),
                        this.getEndCompetenceField(),
                        this.getNameField(),

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
									{
										text: 'Arquivo XLS',
										type: 'XLS',
										iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
										scope: this,
                                        handler:function() { 
                                            this._generateReport(this.XLS_FUNCTION)
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
			   title: 'Relatório Sintetizado de Capacitações'
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

		ceaf.reports.Capacitation.superclass.constructor.call(this, cfg);
	}
});