/*****************************************************************************
*                                                                            *
*                            FOLHA PONTO                          *
*                                                                            *
*****************************************************************************/
Ext._define('rh.pvf.reports.PointSheetReport', {
	extend: 'toolkit.widget.TabPanel',

    BACKGROUND_COLOR: '#005a7d',
    CARD_HEIGHT: 200,
    CARD_WIDTH: 550,
    REGION: 'center',
    GAP: 50,
    LEFT_PADDING: 375,
    BOTTOM_PADDING: 100,

    REPORT_CLASS: 'PointSheetCheckReport',

    PDF_FUNCTION: null,
    XLS_FUNCTION: 'generate_point_sheet_xls',
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
        if(!this._competenceField)
            this._competenceField = Ext._create('Ext.form.TextField', {
                name: 'competence',
                fieldLabel: 'Competência (mm/aaaa)',
                width: 400,
            }, config);

        return this._competenceField;
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
                title: 'Relatório de Entrega de Folhas Ponto',
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
			   title: 'Relatório de Entrega de Folhas Ponto'
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

		rh.pvf.reports.PointSheetReport.superclass.constructor.call(this, cfg);
	}
});