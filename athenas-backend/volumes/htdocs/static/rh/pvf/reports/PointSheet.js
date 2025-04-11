/*****************************************************************************
*                                                                            *
*                            FOLHA PONTO                          *
*                                                                            *
*****************************************************************************/
Ext._define('rh.pvf.reports.PointSheet', {
    extend: 'Ext.form.FormPanel',

    _generatePointSheet: function(){
		if (this.getMonthField().getValue() && this.getYearField().getValue()) {
				Ext.Ajax.request({
					url: toolkit.util.Normalize.controller_action('PointSheetReport', 'create_pdf'),
					params: {
                        month: this.getMonthField().getValue(),
                        year: this.getYearField().getValue()
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
                            this.sendEmiterError(obj)

                            setTimeout( function() {
                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'PointSheetReport',
                                        'marker'
                                    ),
                                    params: {
                                        uuid: obj.uuid
                                    },
                                    success: function() {},
                                    failure: function() {},
                                });
                            },
                            100);
                            
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
				msg: 'Selecione Mês e Ano.',
				icon: Ext.Msg.ERROR,
				buttons: Ext.Msg.OK
			})
	
    },


    sendEmiter: function(obj) {  
        var RemoteObserver = core.RemoteObserver;
        tool = toolkit.util
        var cb = RemoteObserver.on('point-sheet', {
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

                RemoteObserver.un('point-sheet', {scope: this,})
                }else {
                    this.sendEmiter(obj)
                }
            },

        });

    },

    sendEmiterError: function(obj) {  
        var RemoteObserver = core.RemoteObserver;
        tool = toolkit.util
        var cb = RemoteObserver.on('point-sheet-error', {
        scope: this,
        fn: function (data) {
            if(data){
                setTimeout(
                    function() {
                        Ext.Msg.show({
                            title: 'Error',
                            msg: data.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    },
                    100
                );

                RemoteObserver.un('point-sheet-error', {scope: this,})
                }else {
                    this.sendEmiterError(obj)
                }
            },

        });

    },


    getMonthField: function() {
        if (!this._monthfield) {
            this._monthfield = Ext._create('core.fields.ComboField', {
                fieldLabel: "Mês",
                hiddenName: "month",
                value:new Date().getMonth()+1,
                anchor: '99%',
                store:[
                   [1,'JANEIRO'],
                   [2,'FEVEREIRO'],
                   [3,'MARÇO'],
                   [4,'ABRIL'],
                   [5,'MAIO'],
                   [6,'JUNHO'],
                   [7,'JULHO'],
                   [8,'AGOSTO'],
                   [9,'SETEMBRO'],
                   [10,'OUTUBRO'],
                   [11,'NOVEMBRO'],
                   [12,'DEZEMBRO'],
                ],
                autoLoad: true
            });
        }

        return this._monthfield;
    },

    getYearField: function() {
        if (!this._yearfield) {
            this._yearfield = Ext._create('core.fields.ComboField', {
                fieldLabel: "Ano",
                hiddenName: "year",
                anchor: '99%',
                value:new Date().getFullYear(),
                displayField: 'description',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                      url: core.callAction('PointSheetReport', 'get_year')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {name: 'pk', type: 'int'},
                            {name: 'description', type: 'string'},
                        ]
                    })
                }),
                autoLoad: true
            });
        }

        return this._yearfield;
    },


    getGenerateButton: function(cfg) {
        if (this._generateButton) {
            return this._generateButton;
        }

        this._generateButton = Ext._create('Ext.Button', {
            text: 'Gerar',
            scope: this,
            iconCls: 'icon-ged icon-ged-application-pdf',
            handler: this._generatePointSheet
        });

        return this._generateButton;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            border: false,
            labelWidth: 86,
            items: [
                this.getMonthField(cfg),
                this.getYearField(cfg)
            ],
            buttonAlign: 'left',
            buttons: [
                this.getGenerateButton(cfg),
            ],
        });

        rh.pvf.reports.PointSheet.superclass.constructor.call(this, cfg);
    },
});
