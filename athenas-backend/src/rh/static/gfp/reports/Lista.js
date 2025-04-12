Ext._define('rh.gfp.reports.Lista', {
	extend: 'toolkit.widget.TabPanel',

    BACKGROUND_COLOR: '#005a7d',
    CARD_HEIGHT: 530,
    CARD_WIDTH: 550,
    REGION: 'center',
    GAP: 50,
    LEFT_PADDING: 375,
    BOTTOM_PADDING: 100,

    CLASS_NAME: 'ListaReport',
    PDF_FUNCTION: 'generate_lista_pdf',
    XLS_FUNCTION: 'generate_lista_xls',
    CSV_FUNCTION: 'generate_lista_csv',

    _getDefaults: function () {
        return {
            flex: 1,
            height: this.CARD_HEIGHT,
            width: this.CARD_WIDTH,
            baseCls: 'x-river-panel',
            align: this.REGION,
            style: {
                'position': 'initial',
                'margin-top': '2rem'
            },
        };
    },
	_generateReport: function(function_name){
        var params = {
            matricula: this.getMatriculaField().getValue(),
            active: this.getIsActiveField().getValue(),
            type_by_possession: this.getTypeByPossessionField().getValue(),
            end_competence: this.getEndCompetenceField().getValue(),
            start_competence: this.getStartCompetenceField().getValue(),
        };

        selections = this.getTypeByPossessionCheckboxGrid().getSelectionModel().getSelections(),
        params.types_by_possession = selections.map(function (selection) {
            return selection.data.value;
        }).join(',');
        
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                this.CLASS_NAME,
                function_name
            ),
            params: params,
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
                                setTimeout(
                                    function() {
                                        toolkit.util.downloadFile({
                                            url: data.path,
                                            filename: data.filename,
                                            approach: 'download',
                                        });
                                        RemoteObserver.un('base-report', {scope: this})
                                    
                                    },
                                    1000
                                );
                            
                            }
                        });

                        setTimeout( function() {
                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    this.CLASS_NAME,
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

    getMatriculaField: function(config){
        if(!this._matriculaField)
            this._matriculaField = Ext._create('Ext.form.NumberField', {
                name: 'matricula',
                fieldLabel: 'Matrícula',
                width: 400,
            }, config);

        return this._matriculaField;
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

    getIsActiveField: function(config){
        if(!this._isActiveField)
            this._isActiveField = Ext._create('Ext.form.ComboBox', {
                name: 'active',
                fieldLabel: 'Status dos servidores / membros',
                allowBlank: false,
                value: 9999,
                width: 400,
                store: [
                    [9999, 'ATIVOS E INATIVOS'],
                    [ 1, 'ATIVOS'],
                    [ 0, 'INATIVOS']
                ],
                triggerAction: 'all',
                editable: false,
            }, config);

        return this._isActiveField;
    },

    getTypeByPossessionCheckboxGrid: function () {
        if (!this._multiReportGrid) {
            var selectionModel = new Ext.grid.CheckboxSelectionModel({ checkOnly: true });
            this._multiReportGrid = Ext._create('Ext.grid.GridPanel', {
                fieldLabel: 'Tipos de Servidores',
                sm: selectionModel,
                deferRowRender: false,
                stripRows: true,
                style: { border: '1px solid #99bbe8' },
                columnLines: true,
                height: 250,
                anchor: '99%',
                autoExpandColumn: 'description',
                checked: true,
                store: Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('ListaReport', 'employee_type_by_possessions')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            { name: 'value', type: 'string' },
                            { name: 'description', type: 'string' }
                        ]
                    })
                }),
                columns: [
                    selectionModel,
                    { header: 'Sigla', dataIndex: 'value', hidden: true, width: 50 },
                    { header: 'Tipos', dataIndex: 'description', id: 'description' },
                ],
                
            });
        }
        this._multiReportGrid.getStore().on({
            scope: this,
            load: function () {
                this.markAll(this._multiReportGrid);
            }
        });

        return this._multiReportGrid;
    },


    markAll: function (grid) {
        var _data = grid.getStore().data;
        var _selected = [];
        for (i = 0; i <= _data.length; i++) {
            _data.items.map(function (item) {
                    _selected.push(item)
            });
        }
        grid.getSelectionModel().clearSelections();
        grid.getSelectionModel().selectRecords(_selected);
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
                title: 'Lista - Relatório Salarial',
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
                        this.getStartCompetenceField(),
                        this.getEndCompetenceField(),
                        this.getIsActiveField(),
                        this.getTypeByPossessionCheckboxGrid(),
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
										text: 'Arquivo CSV',
										type: 'CSV',
										iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
										scope: this,
                                        handler:function() { 
                                            this._generateReport(this.CSV_FUNCTION)
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
			   title: 'Lista - Relatório Salarial'
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

		rh.gfp.reports.Cubo.superclass.constructor.call(this, cfg);
	}
});