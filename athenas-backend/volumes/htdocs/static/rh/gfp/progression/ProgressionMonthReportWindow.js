
Ext._define('rh.gfp.progression.ProgressionMonthReportWindow', {
    extend: 'Ext.Window',

    title: 'Relatório de Progressões do Mês',

    CLASS_REPORT: 'ProgressionMoveReport',
    FUNCTION_REPORT: 'generate_progression_move_report',

    _defaultOutputFormat: 'PDF',
    
    _listOutputFormat: [
	    {
	        title: 'Arquivo PDF',
	        type: 'PDF',
	        iconCls: 'icon-ged icon-ged-application-pdf'
	    },
        {
	        title: 'Arquivo XLS',
	        type: 'XLS',
	        iconCls: 'icon-ged icon-ged-application-vnd-ms-excel'
	    },
	],

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'panel',
                        frame: true,
                        layout: 'form',
                        items: [
                        {
                            fieldLabel: 'Mês',
                            xtype: 'combo',
                            hiddenName: 'month',
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
                        },
                        {
                            xtype: 'numberfield',
                            fieldLabel: 'Ano',
                            precision: 0,
                            name: 'year'
                        },                    
                    ]
                }
                ]
            });

        return this._formPanel;
    },

	getListOutputFormat: function() {
	    return this._listOutputFormat;
	},

	outputFormat: function() {
        return this._defaultOutputFormat;
    },

	getAllFormatType: function() {
        if(!this._allFormatType) {
            var me = this;
                        
            this._allFormatType = this.getListOutputFormat().map(
                function(item) {
                    return {
                        text: item.title,
                        iconCls: item.iconCls, 
                        handler: function() {
                            me.formatSelected(item.type, item.iconCls);
                        }
                    }  
                }
            );
        }
        
        return this._allFormatType;
    },

    formatSelected: function(format, icon) {
        this._defaultOutputFormat = format.toUpperCase();
        this.getRunReportButton().setIconClass(icon);
        this.generateReport(true);
    },  

    getRunReportButton: function(cfg) {  
        if(!this._runReportSplitBtn) {
            var me = this;
            this._runReportSplitBtn = Ext._create('Ext.Toolbar.SplitButton', {
                text: this._reportButtonText,
                scope: this,
                handler: function() { 
                	me.generateReport(true);
                },
                iconCls: 'icon-ged icon-ged-application-pdf',
                menu : {
                    items: this.getAllFormatType()
                }
            });
        }

        return this._runReportSplitBtn;
    },

    generateReport: function() {
        if(!this.getFormPanel().getForm().isValid())
            return;

        var values = this.getFormPanel().getForm().getValues();
        var output_format = this.outputFormat();
        Ext.Ajax.request({
            scope: this,
            url: toolkit.util.Normalize.controller_action(this.CLASS_REPORT, this.FUNCTION_REPORT),
            disableCaching: false,
            params: Ext.apply(
                values,
                {
                    output_format: output_format,
                    title: this.title
                }
            ),values,
            method: 'POST',
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                if(!obj.success)
                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.OK,
                        buttons: Ext.Msg.ERROR,
                        msg: obj.message
                    });
                    this.close();
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
            },
            failure: function(request) {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Erro de comunicação com servidor, tente novamente mais tarde.'
                });
            }
            
        });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                modal: true,
                border: false,
                width: 600,
                items: [
                    this.getFormPanel(cfg)
                ],
                buttons: [
                    this.getRunReportButton(),
                    {
                        text: 'Limpar',
                        scope: this,
                        handler: function() { this.getFormPanel().getForm().reset();}
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: function() { this.close(); }
                    }
                ]
            }
        );

        rh.gfp.progression.ProgressionMonthReportWindow.superclass.constructor.call(this, cfg);
    }
});
