 Ext._define('rh.pvf.reports.Calendar', {
	extend: 'toolkit.widget.TabPanel',

	_generateCalendar: function(){
        if(this.getMonthField().getValue() && this.getYearField().getValue() && this.getTypeReportField().getValue() && this.getWorkplace().getValue()){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'PVFCalendarRestful',
                    'create_calendar_pdf'
                ),
                params: {
                    month: this.getMonthField().getValue(),
                    year: this.getYearField().getValue(),
                    type_report: this.getTypeReportField().getValue(),
                    team: this.getWorkplace().getValue(),
                },
                success: function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(obj.success)

                       this.sendEmiter(obj)

                        setTimeout( function() {
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                'PVFCalendarRestful',
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
        }else Ext.Msg.show({
            msg: 'Selecione o Ano, Mês e o Tipo para impressão da agenda.',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

    sendEmiter: function(obj) {
            
            var RemoteObserver = core.RemoteObserver;
            tool = toolkit.util
            var cb = RemoteObserver.on('calendar-report', {
            scope: this,
            fn: function (data) {

            if(data){
                setTimeout(
                    function() {
                        Ext.Msg.show({
                            title: 'Agenda',
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                        
                        tool.downloadFile({
                            url: data.path,
                            filename: data.filename,
                            approach: 'download',
                        });
                    },
                    600
                );

                RemoteObserver.un('calendar-report', {scope: this,})
                }else {
                    this.sendEmiter(obj)
                }
            },

        });

    },

    getTypeReportField: function() {
        if (!this._typefield) {
            this._typefield = Ext._create('core.fields.ComboField', {
                fieldLabel: "Tipo",
                hiddenName: "type_report",
                value:1,
                width: 400,
                store:[
                   [1,'Completo'],
                   [2,'Reduzido'],
                ],

                autoLoad: true
            });
        }

        return this._typefield;
    },

    getMonthField: function() {
        if (!this._monthfield) {
            this._monthfield = Ext._create('core.fields.ComboField', {
                fieldLabel: "Referência",
                hiddenName: "month",
                value:new Date().getMonth()+1,
                width: 400,
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
                   [9999,'ANUAL'],
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
                width: 400,
                value:new Date().getFullYear(),
                displayField: 'description',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                      url: core.callAction('PVFCalendarRestful', 'get_year')
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

    getWorkplace: function(cfg){
		if(!this._workplace){
        this._workplace = Ext._create('core.fields.ComboField', {
            fieldLabel: "Equipe",
            hiddenName: "team",
            hidden: cfg.type_employee === "M"?false:true,
            width: 400,
            value: 9998,
            displayField: 'description',
            store: Ext._create('Ext.data.Store', {
                proxy: Ext._create('Ext.data.HttpProxy', {
                  url: core.callAction('PVFCalendarRestful', 'get_teams')
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

		return this._workplace;
	},
    

	getMain: function(cfg){
		if(!this._panel)
		this._panel = new Ext.Panel({
		    layout: 'border',
		    region: 'center',
		    height: 850,
		    split: true,
		    autoEl: {tag: 'center'},
		    items: [
	        {
	        	region: 'center',
	        	border: false,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Impressão da Agenda',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px; margin-top: 2rem;',
	        		align: 'center',
	        		items:[
                        this.getMonthField(),
                        this.getYearField(),
                        this.getTypeReportField(),
                        this.getWorkplace(cfg),
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Agenda',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this._generateCalendar,
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
			   title: 'Agenda'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[ 
					this.getMain(cfg),
				]
			}
		);
        core.RemoteObserver.init()
        obj = {
            message:"Aguarde o sistema fará o download do agenda solicitada.",
        }
        this.sendEmiter(obj)
		rh.pvf.reports.Calendar.superclass.constructor.call(this, cfg);
	}
});