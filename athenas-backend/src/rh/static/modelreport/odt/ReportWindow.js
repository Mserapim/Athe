Ext._define('rh.modelreport.odt.ReportWindow', {
    extend: 'rh.modelreport.odt.Window',

    rest: 'rh.modelreport.odt.Restful',
    width:500,
    height:120,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        name: "employee",
                        fieldLabel: "Servidor",
                        xtype: "rest-autocompletefield",
                        allowBlank: true,
                        anchor:'100%',
                        rest: "rh.employee.Restful",
                        gridConfig: {
                            configOrderToolBar: ['search', '->'],
                            hideColumns: ['departure_unicode', 'elective_unicode', 'pk',  'ativo', 'user', 'tipo', 'pessoa_fisica',
                            'email', 'vpi', 'data_referencia_ferias', 'chefe_imediato', 'chefe_imediato_unicode', 'effective_unicode',
                            'data_exercicio','data_posse', 'data_desligamento', 'created_at', 'modified_at', 'created_by_unicode',
                            'modified_by_unicode','type_by_possession_display', 'event_esocial','commission_unicode' ],
                            columnAction: false,
                        }
                    },
                ]
            });
        return this._formPanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Gerar ODT',
                    type: 'ODT',
                    iconCls: 'icon-ged icon-ged-application-msword',
                    scope: this,
                    handler: function () {
                        this.getReport(cfg,'generate_identification_odt')
                        //this.destroy()
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
        var params = this.getFormPanel().getForm().getValues();
		if (params.employee) {
            console.log(method)
            
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action('IdentificationOdt', method),
                params: {
                    template:cfg.selected.data.template,
                    name:cfg.selected.data.name,
                    employee:params.employee
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
                        this.sendEmiter(obj)
                        
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
				msg: 'Selecione um servidor',
				icon: Ext.Msg.ERROR,
				buttons: Ext.Msg.OK
			})
	
    },


    sendEmiter: function(obj) {  
        var RemoteObserver = core.RemoteObserver;
        tool = toolkit.util
        var cb = RemoteObserver.on('base-report', {
        scope: this,
        fn: function (data) {

            if(data){
                setTimeout(
                    function() {
                        
                        tool.downloadFile({
                            url: data.path,
                            filename: data.filename,
                            approach: 'download',
                        });
                    },
                    100
                );

                RemoteObserver.un('base-report', {scope: this,})
                }else {
                    this.sendEmiter(obj)
                }
            },

        });

    },


    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            title: 'Modelo PDF',
            items: this.getFormPanel(cfg)
        });

        Ext.apply(cfg, {
          
        });

        rh.modelreport.odt.ReportWindow.superclass.constructor.call(this, cfg);
    }


});