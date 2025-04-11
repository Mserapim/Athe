
 Ext._define('rh.cadastralquality.OpenReportWindow', {
    extend: 'rh.cadastralquality.Window',

    rest: 'rh.cadastralquality.Restful',
    width:300,

    
    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        hiddenName:'orientation',
                        fieldLabel:"Modo",
                        xtype:'choicefield',
                        choiceId:'queryregistration.PAGE_ORIENTATION',
                        anchor: '99%',
                        readOnly:true,
                        allowBlank: true,
                        value:2
                    },
                ]
            });

        return this._formPanel;
    },


    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Relatório',
                    width: 100,
                    height: 25,
                    scope: this,
                    menu:{
                        scope: this,
                        items: [
                            {
                                text: 'Arquivo PDF ',
                                type: 'PDF',
                                iconCls: 'icon-ged icon-ged-application-pdf',
                                scope: this,
                                handler: function () {
                                    this.getReport(cfg,'create_pdf')
                                    this.destroy()
                                    //console.log(this.getFormPanel().getForm().getValues())
                                }
                            },
                            {
                                text: 'Arquivo XLS',
                                type: 'XLS',
                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                scope: this,
                                handler: function (item) {
                                    this.getReport(cfg,"create_xls")
                                    this.destroy()
                                }
                            },
                        ]
                    }
                },            
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

        return this._buttons;
    },

  

    getReport: function(cfg,method){
		if (params) {
				Ext.Ajax.request({
					url: toolkit.util.Normalize.controller_action('CQualityReport', method),
					params: {
                        pk:cfg.pk
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
                            this.scope.getStore().reload();
                            if (obj.download)
                                var RemoteObserver = core.RemoteObserver;
                                var cb = RemoteObserver.on('query-report', {
                                    scope: this,
                                    fn: function (data) {
                                        setTimeout(
                                            function() {
                                                toolkit.util.downloadFile({
                                                    url: data.path,
                                                    filename: data.filename,
                                                    approach: 'download',
                                                });;
                                                RemoteObserver.un('query-report', {scope: this})
                                            
                                            },
                                            1000
                                        );
                                    
                                    }
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
				msg: 'Primeiro selecione os parâmetros',
				icon: Ext.Msg.ERROR,
				buttons: Ext.Msg.OK
			})
	
    },

    
    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            title: 'Relatório',
            items: this.getFormPanel(cfg)
        });

        Ext.apply(cfg, {
          
        });

        rh.cadastralquality.OpenReportWindow.superclass.constructor.call(this, cfg);
    }


});