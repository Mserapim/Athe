/**
 *
 **/
Ext._define('adm.patrimonio.SuspensaoManage', {
    extend: 'Ext.Panel',

    getGridPanel: function(cfg) {
        if(!this._gridPanel) {
            this._gridPanel = Ext._create('adm.patrimonio.SuspensaoGrid', {
                region: 'center',
                title: '',
                minHeight: 195,
                grudAutoLoad: false
            });

            this._gridPanel.setParam('nota_entrada', cfg.nota_entrada);
            this._gridPanel.setFilterProperty('nota_entrada__id', cfg.nota_entrada, 1000);

            this._gridPanel.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.selected(record);
                },
                rowdeselect: function(sm, index, record) {
                    this.selected(undefined);
                }
            });
        }

        return this._gridPanel;
    },

    getDisplayPanel: function() {
        if(!this._displayPanel)
            this._displayPanel = Ext._create('Ext.Panel', {
                region: 'south',
                minHeight: 195,
                split: true,
                height: 545
            });

        return this._displayPanel;
    },

    selected: function(value) {
        if(value !== undefined) {
            this._selected = value;
            this.observe();
        }

        return this._selected;
    },

    observe: function() {
        this.getDisplayPanel().removeAll();

        if(this.selected()) {
            this.getDisplayPanel().enable();
            this.getDisplayPanel().add(
                Ext._create('Ext.Panel', {
                    html: this.selected().get('justificativa'),
                    padding: 5,
                    border: false
                })
            );
        }
        else {
            this.getDisplayPanel().disable();
        }

        this.getDisplayPanel().doLayout();
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getGridPanel(cfg),
                    this.getDisplayPanel()
                ]
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.SuspensaoManage.superclass.constructor.call(this, cfg);
        this.on({
            scope: this,
            render: this.observe
        });
    }
});
