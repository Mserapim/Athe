/**
 *
 **/
Ext._define('core.fields.AutocompleteSelectionWindow', {
    extend: 'Ext.Window',

    getGridPanel: function(cfg) {
        if(!this._gridPanel) {
            var values = core.nullValue(cfg.values, []);
            var preCfg = core.nullValue(cfg.gridConfig, {});
            var listeners = core.nullValue(preCfg.listeners, false);

            if(listeners) preCfg.listeners = null;

            var self = this;

            Ext.apply(preCfg, {
                region: 'center',
                border: false,
                safeMode: cfg.safeMode,
                sm:  Ext._create('Ext.grid.RowSelectionModel', {
                    singleSelect: !cfg.multi
                }),
                viewConfig: {
                    scope: this,
                    getRowClass: function(record) {
                        if(values.indexOf(record.get(self.valueField)) >= 0) {
                            return 'x-grid3-unabled';
                        }
                    }
                }
            });

            if(cfg.safeMode)
                preCfg.gridAutoLoad = false;

            this._gridPanel = core.RestfulGrid.factoryGrid(
                cfg.rest,
                preCfg
            );

            this._gridPanel.searchCount = 0;
            Ext.override(
                this._gridPanel,
                {

                }
            );

            if(listeners)
                this._gridPanel.on(listeners);

            Ext.each(
                core.nullValue(cfg.gridConfig.preFilter, []),
                function(item) {
                    this.setFilterProperty(
                        item.property,
                        item.value,
                        core.nullValue(item.stage, 1000),
                        (item.autoload === undefined ? true : item.autoload)
                    );
                },
                this._gridPanel
            );
        }

        return this._gridPanel;
    },

    commitSelection: function(close) {
        close = core.nullValue(close, false);

        if(this.multi)
            this.__commitMultiSelection(close);
        else
            this.__commitSingleSelection();
    },

    __commitSingleSelection: function() {
        var selection = this.getGridPanel().getSelectionModel().getSelected();

        if(selection)
            this.field.setValue(selection.get(this.valueField));

        this.destroy();
    },

    __commitMultiSelection: function(close) {
        console.warn('não foi implementado ainda.');
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() { this.commitSelection(true); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

            if(cfg.multi)
                this._buttons.insert(
                    1,
                    {
                        text: 'Selecionar e fechar',
                        scope: this,
                        handler: function() { this.commitSelection(false); }
                    }
                );
        }

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        if(!cfg.rest)
            throw 'Você deve informar o restful que corresponde a entidade que deseja selecionar';

        var box = Ext.getBody().getBox();

        Ext.applyIf(
            cfg,
            {
                title: 'Selecionar',
                multi: false,
                width: box.width * 0.75,
                height: box.height * 0.75,
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGridPanel(cfg),
                buttons: this.getButtons(cfg)
            }
        );

        // this.callParent([cfg]);
        core.fields.AutocompleteSelectionWindow.superclass.constructor.call(this, cfg);
    }
});
