/**
 *
 **/
Ext._define('adm.patrimonio.movimento.LogStatusManage', {
    extend: 'Ext.Panel',

    getDisplayPanel: function() {
        if(!this._displayPanel)
            this._displayPanel = Ext._create('Ext.Panel', {
                region: 'south',
                split: true,
                height: 180,
                layout: 'hbox',
                bodyStyle: {
                    padding: '5px'
                },
                autoScroll: true
            });

        return this._displayPanel;
    },

    getGridPanel: function() {
        if(!this._gridPanel) {
            this._gridPanel = Ext._create('adm.patrimonio.movimento.LogStatusGrid', {
                region: 'center',
                columAction: false
            });

            this._gridPanel.createItem = this._gridPanel.updateItem = this.removeItems = function() {};
        }

        return this._gridPanel;
    },

    displayComment: function(statusLog) {
        this.getDisplayPanel().removeAll();

        if(statusLog) {
            this.getDisplayPanel().add(
                Ext._create('Ext.Panel', {
                    border: false,
                    preventBodyReset: true,
                    html: statusLog.get('comentario')
                })
            );
            this.getDisplayPanel().doLayout();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {

            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGridPanel(),
                    this.getDisplayPanel()
                ]
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.movimento.LogStatusManage.superclass.constructor.call(this, cfg);

        this.getGridPanel().getSelectionModel().on({
            scope: this,
            rowselect: function(sm, index, record) {
                this.displayComment(record);
            },
            rowdeselect: function(sm) {
                this.displayComment(undefined);
            }
        });
    }
});
