/**
 *
 **/
Ext._define('rh.jobpositiontable.reportWindow', {
	extend: 'Ext.Window',

    

    constructor: function(cfg) {
		cfg = cfg ? cfg : {};
        params = cfg.params;

		Ext.applyIf(
			cfg,
			{
			   title: 'Gerar Relatório',
               width: 650,
               height: 400,
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
		rh.jobpositiontable.reportWindow.superclass.constructor.call(this, cfg);
	},

    _cargosFiltro: function(){
        let selecoes = this._multiReportGrid?.getSelectionModel()?.getSelections();
        let cargos = [];
        selecoes.forEach( function(selecao){
            cargos.push(selecao.data.value)
        })
        return cargos;
    },

    _gerarRelatorio: function(formato, tipoRelatorio){
        let classeRelatorio = 'CargoQuadroRelatorioSintetico';
        if (tipoRelatorio == 'analitico'){
            classeRelatorio = 'CargoQuadroRelatorioAnalitico';
        }
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(classeRelatorio, 'generate_report'),
            params: {
                filtros: this.params.filter,
                keyword: this.params.keyword,
                formato: formato,
                cargos: this._cargosFiltro(),
            },
            method: 'GET',
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
                                                    classeRelatorio,
                                                    'marker'
                                                ),
                                                params: {
                                                    uuid: obj.uuid,
                                                    formato: formato
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

    getOriginCheckboxGrid: function (params) {

        if (!this._multiReportGrid) {
            var selectionModel = new Ext.grid.CheckboxSelectionModel({ checkOnly: true });
    
            let proxy = Ext._create('Ext.data.HttpProxy', {
                url: core.callAction('CargoQuadroRelatorioSintetico', 'lista_cargos'),
                method: 'GET',
                listeners: {
                    'beforeload': function (proxy, options) {
                        options.params = Ext.apply(options.params || {}, {
                            filtros: JSON.stringify(params.filter || []),
                            keyword: params.keyword
                        });
                    },
                    scope: this
                }
            });
            
            this._multiReportGrid = Ext._create('Ext.grid.GridPanel', {
                fieldLabel: 'Cargos',
                sm: selectionModel,
                deferRowRender: false,
                stripeRows: true,
                style: { border: '1px solid #99bbe8' },
                columnLines: true,
                height: 250,
                width: 400,
                anchor: '99%',
                autoExpandColumn: 'description',
                checked: true,
                store: Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: proxy,
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            { name: 'value', type: 'string' },
                            { name: 'description', type: 'string' }
                        ]
                    }),
                    baseParams: {
                        filtros: JSON.stringify(params.filter || []),
                        keyword: params.keyword
                    }
                }),
                columns: [
                    selectionModel,
                    { header: 'Sigla', dataIndex: 'value', hidden: true, width: 50 },
                    { header: 'Tipos', dataIndex: 'description', id: 'description' },
                ],
            });
        }
    
        return this._multiReportGrid;
    },
    


    getMain: function (cfg) {

        if (!this._panel) {
            this._panel = new Ext.Panel({
                layout: 'border',
                region: 'center',
                height: 650,
                split: true,
                autoEl: { tag: 'center' },
                items: [
                    {
                        region: 'center',
                        border: false,
                        autoScroll: true,
                        items: [
                        {
                            xtype: 'fieldset',
                            title: 'Relatório Cargos em Quadro',
                            name: 'fieldServidor',
                            width: "33%",
                            style: 'margin: 5px',
                            align: 'center',
                            items:[
                                {
                                    xtype: 'radiogroup',
                                    fieldLabel: 'Relatório',
                                    columns: 2,
                                    vertical: false,
                                    style: 'margin-top: 10px;',
                                    name: 'reportFormat',
                                    items: [
                                        { boxLabel: 'Sintético', name: 'tipoRelatorio', inputValue: 'sintetico', checked: true },
                                        { boxLabel: 'Analítico', name: 'tipoRelatorio', inputValue: 'analitico' }
                                    ]
                                },
                                this.getOriginCheckboxGrid(cfg.params),
                                {
                                    xtype: 'button',
                                    iconCls: 'icon-siatu icon-siatu-move-down',
                                    style: 'margin-top: 10px; margin-left: 50px',
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
                                                handler: function (item) {
                                                    var radioGroup = this._panel.items.get(0).items.get(0).items.get(0);
                                                    var selected = radioGroup.getValue().inputValue;
                                                    this._gerarRelatorio('PDF', selected)
                                                }
                                            },
                                            {
                                                text: 'Arquivo XLS',
                                                type: 'XLS',
                                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                scope: this,
                                                handler: function (item) {
                                                    var radioGroup = this._panel.items.get(0).items.get(0).items.get(0);
                                                    var selected = radioGroup.getValue().inputValue;
                                                    this._gerarRelatorio('XLS', selected)
                                                }
                                            },
                                        ]
                                    },
                                }
                            ]
                        },
                        ]
                    }
                ]
            });
        }
    
        return this._panel;
    },
    
    

});
