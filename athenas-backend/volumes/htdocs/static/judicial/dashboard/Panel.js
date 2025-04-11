
Ext._define('judicial.dashboard.Panel', {
    extend: 'Ext.Container',

    factoryRefreshFn: function(grid, rest, counters) {
        var mapTitle = {};

        counters.forEach(
            function(counter) {
                mapTitle[counter.name] = counter.title;
            }
        );

        return function() {
            var restObj = Ext._create(rest);
            var rules = (grid.$rules || false);
            var store = grid.getStore();
            var mask = new Ext.LoadMask(grid.getEl(), {msg: 'Buscando informações...'});

            if(!rules) {
                rules = {};

                counters.forEach(
                    function(counter) {
                        rules[counter.name] = counter.filter;
                    }
                );

                grid.$rules = rules;
            }

            mask.show();
            store.removeAll();
            restObj.doRequest(restObj.getRoute('count', null, 'GET', {
                params: { rules: Ext.encode(rules) },
                callback: function() {
                    mask.hide();
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        store.add(
                            rst.collection.map(
                                function(counter) {
                                    counter.title = (mapTitle[counter.name] || 'undefined');
                                    return new Ext.data.Record(counter);
                                }
                            )
                        );
                    }
                },
                failure: function(xhr) {
                    console.log('falhou');
                }
            }));
        };
    },

    factoryPanel: function(cfg, panelConfig) {
        var store = Ext._create('Ext.data.ArrayStore', {
            fields: ['id', 'name', 'counter', 'title'],
            data: []
        });

        var grid = Ext._create('Ext.grid.GridPanel', {
            collapsible: true,
            title: (panelConfig.title || 'undefined'),
            width: panelConfig.width,
            colspan: panelConfig.colspan,
            autoExpandColumn: 'autoExpand',
            store: store,
            hideHeaders: true,
            listeners: {
                scope: this,
                afterRender: function() {
                    refresh();
                },
                dblclick: function(data) {
                    var selection = grid.getSelectionModel().getSelections();

                    if(selection.length > 0) {
                        var name = selection[0].get('name');
                        var counter = null;

                        panelConfig.counters.forEach(
                            function(c) {
                                if(c.name === name) {
                                    counter = c;
                                }
                            }
                        );

                        if(counter && counter.callback) {
                            core.invokeCallback(counter.callback, counter);
                        } else if(counter && !counter.callback) {
                            console.warn('Counter callback for "%s" not configured!', name);
                        } else {
                            console.warn('Counter for "%s" not found!', name);
                        }
                    }
                }
            },
            bbar: [
                '->',
                '-',
                {
                    iconCls: 'icon-core icon-core-refresh',
                    text: 'Atualizar',
                    handler: function() { refresh(); }
                },
                '-'
            ],
            cm: Ext._create('Ext.grid.ColumnModel', [
                {
                    header: 'Propriedade',
                    id: 'autoExpand',
                    dataIndex: 'title'
                },
                {
                    header: 'Contador',
                    dataIndex: 'count',
                    width: 60,
                    renderer: function(value) {
                        return [
                            '<div style="text-align: right; margin-right: 3px">',
                                value,
                            '</div>'
                        ].join('');
                    }
                }
            ])
        });

        var refresh = this.factoryRefreshFn(
            grid,
            panelConfig.rest,
            panelConfig.counters);

        return grid;
    },

    factoryPanels: function(cfg, panels) {
        var vm = this;

        return panels.map(
            function(panelConfig) {
                return vm.factoryPanel(cfg, panelConfig);
            }
        );
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(cfg, {
            layout: {
                type: 'table',
                tableAttrs: (cfg.tableAttrs || {}),
                columns: (cfg.columns || 2)
            },
            defaults: {
                height: (cfg.cellHeight || 250),
                style: {
                    margin: '2px'
                }
            },
            items: this.factoryPanels(cfg, cfg.panels || [])
        });

        judicial.dashboard.Panel.superclass.constructor.call(this, cfg);
    }
});
