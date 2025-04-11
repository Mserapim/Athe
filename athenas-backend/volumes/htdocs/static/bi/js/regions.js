Ext.ns('toolkit.bi');

toolkit.bi.Regions = Ext.extend(Ext.Window, {

    constructor: function()
    {
        var options = {
            title: 'Lista de Comarcas',
            modal:true,
            layout:'fit',
            height: 350,
            width: 500,
        };
        toolkit.bi.Regions.superclass.constructor.call(this, options);
        this.add(this._getGrid());
    },

    _getStore: function()
    {
        if(!this.store)
        {
            this.store = new Ext.data.JsonStore({
                autoLoad:true,
                root: 'list',
                totalProperty: 'total',
                fields: ['athenas_id', 'name'],
                proxy: new Ext.data.HttpProxy({
                    method:'GET',
                    url: action('BI/regions/json')
                }),
            });
            new Ext.LoadMask(Ext.getBody(), {msg:'Por favor aguarde...', store:this.store, removeMask:true});
        }
        return this.store;
    },

    _getGrid: function()
    {
        if(!this.grid)
        {
            this.grid = new Ext.grid.GridPanel({
                title:'Clique duas vezes sobre uma comarca para visualizar os dados',
                width:350,
                store: this._getStore(),
                columns:[{ header:'Comarca', dataIndex:'name', width:450 }],
                sm: new Ext.grid.RowSelectionModel({ singleSelect:true }),
                listeners:{
                    dblclick: function()
                    {
                        var record = this.grid.getSelectionModel().getSelected();
                        //alert('Carregar relatório da comarca '+ record.get('name'));
                        new toolkit.bi.RegionCharts(record.get('athenas_id')).show();
                        this.hide();
                        this.destroy();
                    },
                    scope: this
                }
            });
        }
        return this.grid;
    }
});

toolkit.bi.RegionCharts = Ext.extend(Ext.Panel, {

    constructor: function(region)
    {
        this.region = region;
        var options = {
            closable:true,
            title: 'Relatório Sintético',
            tbar:[
                {
                    text: 'Selecionar Comarca',
                    handler: function()
                    {
                        toolkit.bi.regions = new toolkit.bi.Regions();
                        toolkit.bi.regions.show();
                    }
                }
            ],
            autoScroll: true
        };

        toolkit.bi.RegionCharts.superclass.constructor.call(this, options);
        toolkit.Application.tabspace.add(this);
        this.add(this._getForm());
    },

    _getData:function(response)
    {
        var data = Ext.decode(response.responseText);
        this.add(this._getCharts(data.reports));
        this.doLayout();
        this.loading.hide();
    },

    _getCharts: function(data)
    {
        var regions = [];
        Ext.each(data,
            function(item)
            {
                var charts = [];
                Ext.each(item.data,
                    function(chart)
                    {
                        var _store = new Ext.data.JsonStore({
                            autoLoad:true,
                            data:chart.periods,
                            fields:['period', 'value', 'human_value']
                        });
                        var _chart = new Ext.chart.ColumnChart({
                            store: _store,
                            height:180,
                            width:230,
                            xField: 'period',
                            yField: 'value',
                            tipRenderer : function(chart, record, index, series){
                                return record.data.human_value;
                            }
                        });
                        var _panel = new Ext.Panel({
                            title:chart.name,
                            height:220,
                            items:[_chart]
                        });
                        charts[charts.length] = _panel;
                    }
                );
                var _region = new Ext.Panel({
                    title:item.region,
                    layout:'hbox',
                    margins: '5 5 5 5 ',
                    //autoScroll:true,
                    width:1380,
                    items:charts
                });
                regions[regions.length] = _region;
            }
        );

        return new Ext.Panel({
            id:'reports-panel',
            title: 'Relatórios',
            frame: true,
            items: regions,
            width:1400
            //autoScroll:true
        });
    },

    _getStoreMonths: function()
    {
        var months = [
            [1, 'Janeiro'], [2, 'Fevereiro'], [3, 'Março'], [4, 'Abril'],
            [5, 'Maio'], [6, 'Junho'], [7, 'Julho'], [8, 'Agosto'],
            [9, 'Setembro'], [10, 'Outubro'], [11, 'Novembro'], [12, 'Dezembro'],
        ];

        return new Ext.data.ArrayStore({
            autoDestroy:true,
            data: months,
            fields:['id', 'month']
        });
    },

    _getStoreYears: function()
    {
        var years = [], i;
        for(i=new Date().getFullYear(); i >= 1989 ; i--)
            years[years.length] = [i, i];

        return new Ext.data.ArrayStore({
            autoDestroy:true,
            data: years,
            fields:['id', 'year']
        });
    },

    _getForm: function()
    {
        var month = new Date().getMonth()+1;
        var year = new Date().getFullYear();

        var form = new Ext.form.FormPanel({
            title:'Formulário',
            layout:'hbox',
            border:false,
            width:1400,
            defaults:{ margins:'5 5 5 5' },
            items:[
                {
                    xtype:'fieldset',
                    title:'Meses',
                    width:560,
                    items:[
                        {
                            xtype:'hidden',
                            name:'region',
                            value: this.region
                        },
                        {
                            xtype:'compositefield',
                            fieldLabel:'Mês 1',
                            items:[
                                {
                                    xtype:'combo',
                                    hiddenName:'month',
                                    mode:'local',
                                    triggerAction: 'all',
                                    store: this._getStoreMonths(),
                                    valueField: 'id',
                                    displayField:'month',
                                    value: ((month-1) == 0) ? 12 : month-1
                                },
                                {
                                    xtype:'combo',
                                    hiddenName:'year',
                                    mode:'local',
                                    triggerAction: 'all',
                                    store: this._getStoreYears(),
                                    valueField: 'id',
                                    displayField:'year',
                                    value: ((month-1) == 0) ? year-1 : year
                                }
                            ]
                        },

                        {
                            xtype:'compositefield',
                            fieldLabel:'Mês 2',
                            items:[
                                {
                                    xtype:'combo',
                                    hiddenName:'month2',
                                    mode:'local',
                                    triggerAction: 'all',
                                    store: this._getStoreMonths(),
                                    valueField: 'id',
                                    displayField:'month',
                                    value: month
                                },
                                {
                                    xtype:'combo',
                                    hiddenName:'year2',
                                    mode:'local',
                                    triggerAction: 'all',
                                    store: this._getStoreYears(),
                                    valueField: 'id',
                                    displayField:'year',
                                    value: year
                                }
                            ]
                        }
                    ]

                },
                {
                    xtype:'fieldset',
                    title:'Comparar com',
                    width:235,
                    height:88,
                    items:[
                        {
                            xtype:'combo',
                            hideLabel:true,
                            hiddenName:'region2',
                            mode:'local',
                            triggerAction:'all',
                            store: toolkit.bi.regions.store,
                            valueField: 'athenas_id',
                            displayField:'name',
                            value: this.region
                        },
                        {
                            xtype:'button',
                            text:'Gerar gráficos',
                            width:80,
                            handler: function()
                            {
                                this.loading = new Ext.LoadMask(Ext.getBody(), {msg:'Por favor aguarde...', removeMask:true});
                                this.loading.show();

                                form.getForm().submit({
                                    url:action('BI/simple_report/json'),
                                    timeout:60000,
                                    success: function(form, action)
                                    {
                                        var reportsPanel = this.findById('reports-panel');
                                        if( reportsPanel )
                                            reportsPanel.destroy();

                                        this.add(this._getCharts(action.result.reports));
                                        this.doLayout();
                                        this.loading.hide();
                                    },
                                    failure: function(form, action)
                                    {
                                        this.loading.hide();
                                        switch (action.failureType)
                                        {
                                            case Ext.form.Action.CLIENT_INVALID:
                                                Ext.Msg.alert('Falha', 'Preencha corretamente os campos do formulário.');
                                                break;
                                            case Ext.form.Action.CONNECT_FAILURE:
                                                Ext.Msg.alert('Falha', 'A requisição falhou!');
                                                break;
                                            case Ext.form.Action.SERVER_INVALID:
                                                console.log(action);
                                                Ext.Msg.alert('Falha', 'Sem dados para serem exibidos.');
                                       }
                                    },
                                    scope:this
                                });
                            },
                            scope:this
                        }
                    ]
                }
            ]
        });

        return form;
    }

});
