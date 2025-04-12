Ext._define('rh.pvf.sendtelework.DetailWindow', {
    extend:'rh.pvf.portalrequest.DetailWindow',

    rest: 'rh.pvf.sendtelework.Restful',

    height: 720,

    getFieldSet:function(cfg){
        return this.getMarkTeleworkFieldSet(cfg)
    },

    getMarkTeleworkFieldSet: function (cfg) {
        if (!this._marked)
            this._marked = Ext._create('Ext.form.FieldSet', {
                title: 'Metas',
                items: [
                    this.getMarkTeleworkGrid(cfg)
                ]
            });

        return this._marked;
    },


    getMarkTeleworkGrid: function(cfg) {
        if(!this._markworkGrid) {
            this._markworkGrid = Ext._create('rh.pvf.sendtelework.MarkTeleworkGrid',{
                hideItemsToolbar: [],
                columnAction: false,
                region: 'center',
                height: 150,
                border: false,
                scope: this,
                //doubleClickHandler: function () { },
                configOrderToolBar: [],
            });
        }
        this._markworkGrid.setFilterProperty('request__pk', cfg.data.pk)
        this._markworkGrid.setParam('status',cfg.data.status)
        return this._markworkGrid;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                tabPanelHeight: 620,
                height: 650,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getManagerPanel(cfg),
                    //this.getPendingPanel(cfg)
                ]
            });

        return this._tabPanel;
    },

    getManagerPanel: function (cfg) {
        if (!this._managementPanel)
            this._managementPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                title: 'Principal',
                layout: 'form',
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Informações:',
                        layout: 'column',
                        border: true,
                        items: [
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Data da solicitação: ',
                            },
                            {
                                columnWidth: cfg.data.acquisitive_period?.3:.8,
                                xtype: 'displayfield',
                                fieldLabel: 'Data da solicitação:',
                                style: {fontSize: '12px',marginBottom: '12px'},
                                value: Ext.util.Format.date(cfg.data.date, 'd/m/Y')
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Período Aquisitivo: ',
                                hidden:cfg.data.acquisitive_period?false:true,
                            },
                            {
                                columnWidth: .3,
                                fieldLabel: 'Período Aquisitivo',
                                xtype: 'displayfield',
                                style: {fontSize: '12px', marginBottom: '12px'},
                                value:cfg.data.acquisitive_period,
                                hidden:cfg.data.acquisitive_period?false:true,
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Tipo: ',
                            },
                            {
                                columnWidth: .8,
                                fieldLabel: 'Tipo',
                                style: {fontSize: '12px',marginBottom: '12px'},
                                xtype: 'displayfield',
                                value:cfg.data.type_of_request
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Solicitante: ',
                            },
                            {
                                columnWidth: .8,
                                fieldLabel: 'Solicitante',
                                style: {fontSize: '12px',marginBottom: '12px'},
                                xtype: 'displayfield',
                                value: cfg.data.employee_unicode
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                hidden:cfg.data.custom_approver_current?false:true,
                                value: 'Aprovador Atual: ',
                            },
                            {
                                fieldLabel: 'Aprovador Atual',
                                xtype: 'displayfield',
                                columnWidth: .8,
                                style: {fontSize: '12px',marginBottom: '12px'},
                                hidden:cfg.data.custom_approver_current?false:true,
                                value:cfg.data.custom_approver_current
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Situação: ',
                            },
                            {
                                fieldLabel: 'Situação',
                                xtype: 'displayfield',
                                columnWidth: .8,
                                style: {fontSize: '12px',marginBottom: '12px'},
                                value:cfg.data.status_display
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                hidden:!cfg.data.parcel_number?true:false,
                                value: 'Nº Parcelas: ',
                            },
                            {
                                fieldLabel: 'Nº Parcelas',
                                xtype: 'displayfield',
                                columnWidth: .8,
                                style: {fontSize: '12px',marginBottom: '12px'},
                                hidden:!cfg.data.parcel_number?true:false,
                                value:cfg.data.parcel_number
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px',color:'red',fontWeight:'bold'},
                                value: 'Referência: ',
                            },
                            {
                                xtype: 'displayfield',
                                columnWidth: .8,
                                style: {fontSize: '12px',marginBottom: '12px',color:'red',fontWeight:'bold'},
                                value:cfg.data.reference_month+'/'+cfg.data.reference_year
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Relatório Folha Ponto: ',
                            },
                            this.getGenerateButton(cfg),
                            {
                                columnWidth: .6,
                                xtype: 'displayfield',
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Relatório Teletrabalho: ',
                            },
                            this.getGenerateTeleworkReportButton(cfg),
                        ]
                    },
                    this.getFieldSet(cfg),
                    this.getTabHistory(cfg),
                    
                ]
            });
        return this._managementPanel;
    },

    getPendingPanel: function (cfg) {
        if (!this._pendinPanel)
            this._pendinPanel = Ext._create('Ext.Panel', {
                title: 'Pendências',
                layout:"form",
                frame: true,
                border: false,
                height: 300,
                items: [
                    this.getPendingField(cfg),
                ]
            });
            if(cfg.data.buttons)
                if(cfg.data.buttons == "effective_point")
                    this._pendinPanel.enable();
                else
                    this._pendinPanel.disable();
            else
                this._pendinPanel.disable();
            

        return this._pendinPanel;
    },

    getPendingField: function (cfg) {
        if (!this._pendingField)
            this._pendingField = Ext._create('Ext.form.FieldSet', {
                title: 'Pendências',
                items: [
                    this.getGridPending(cfg)
                ]
            });

        return this._pendingField;
    },

    dataStore:function(cfg){
        return new Ext.data.Store({
            proxy: new Ext.data.HttpProxy({
                url: toolkit.util.Normalize.controller_action('PVFSendPointSheet', 'pending',[cfg.data.employee,cfg.data.reference_month,cfg.data.reference_year,cfg.data.pk]),
                method: 'GET',
                disableCaching: false,
                autoLoad:true,
            }),
            reader: new Ext.data.JsonReader({
                totalProperty: 'total',
                root: 'collection',
                fields: [
                    {name:'type', type: 'string'},
                    {name:'value', type:'string'}
                ]
            }),
            autoLoad:true,
        })
    },

    getGridPending: function(cfg) {
        if(!this._gridPending)
            this._gridPending = new Ext.grid.GridPanel({
                store:this.dataStore(cfg),
                columns: [
                    { header: 'Tipo', dataIndex: 'type', width:150},
                    { header: 'Descrição', dataIndex: 'value', width: 150 },
                ],
                height: 100,
                autoload:true,
                viewConfig: {
                    forceFit: true,
                    getRowClass: function(record, index) {
                        return 'x-grid3-red';
                    }
                },
               
            });

        return this._gridPending;
    },

    getGenerateButton: function(cfg) {
        this._generateButton = Ext._create('Ext.Button', {
            text: 'Clique aqui para baixar',
            scope: this,
            height:20,
            columnWidth: .2,
            iconCls: 'icon-ged icon-ged-application-pdf',
            handler: function() { this._generatePointSheet(cfg) }
            
        });

        return this._generateButton;
    },

    getGenerateTeleworkReportButton: function(cfg) {
        this._generateButton = Ext._create('Ext.Button', {
            text: 'Clique aqui para baixar',
            scope: this,
            height:20,
            columnWidth: .2,
            iconCls: 'icon-ged icon-ged-application-pdf',
            handler: function() { this._generateTeleworkReport(cfg) }
            
        });

        return this._generateButton;
    },

    _generateTeleworkReport: function(cfg){
        console.log('cfg.data')
        console.log(cfg.data)
        var plan_work_id = cfg.data.plan_work_id
        var send_telework_id = cfg.data.pk
        var employee = cfg.data.employee

        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('TeleWorkReport', 'generate_report'),
            params: {
                plan_work_id: plan_work_id,
                send_telework_id: send_telework_id,
                employee: employee
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
                                                    'TeleWorkReport.',
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
            failure: function (request) {
                Ext.Msg.show({
                    msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                })
            },
            scope: this
        });
    },

    _generatePointSheet: function(cfg){
        var month = cfg.data.reference_month
        var year = cfg.data.reference_year
        var employee = cfg.data.employee
		if (month && year) {
				Ext.Ajax.request({
					url: toolkit.util.Normalize.controller_action('PointSheetReport', 'create_pdf'),
					params: {
                        month: month,
                        year: year,
                        employee: employee
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

    getApproverButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [];
            if(!cfg.disableSave)
            if (cfg.data.approver_request){
                this._buttons.push( 
                    new Ext._create('Ext.Button', {
                        text: 'Devolver ao Solicitante',
                        scope: this,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'approver_work'?false:true,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { this.returnApplicant(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Aprovar',
                        hidden:cfg.data.buttons == 'approver_work'?false:true,
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                        handler: function() { this.grantRequest(cfg) }
                            
                    }),
                )
            }
               
        
        }

        if(cfg.status_hidden.includes(cfg.data.status)){
            this._buttons = []
        }else{
            if(!cfg.data.approver_request && cfg.group_dgp){
                this._buttons = [
                    new Ext._create('Ext.Button', {
                        text: 'Cancelar Solicitação',
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/denied.png',
                        handler: function() { this.cancel(cfg)}
                            
                    })
                ] 
            
            }else if(cfg.data.approver_request && cfg.group_dgp){
                this._buttons.push(
                    new Ext._create('Ext.Button', {
                        text: 'Cancelar Solicitação',
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/denied.png',
                        handler: function() { this.cancel(cfg)}
                            
                    })
                )
            }
        }
        return this._buttons;

    },

   

});