/**
 *
 **/
Ext._define('judicial.diligencetemplate.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getDiligenceTemplate: function() {
        if(!this._templateGrid) {
            this._templateGrid = Ext._create('judicial.diligencetemplate.DiligenceTemplateGrid', {
                region: 'center',
                minWidth: 500
            });

            this._templateGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    // this.county(data.get('pk'));
                },
                rowdeselect: function() {
                    // this.county(null);
                }
            });
        }

        return this._templateGrid;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor Templates Diligências'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getDiligenceTemplate()
                ]
            }
        );

        // this.callParent([cfg]);
        judicial.diligencetemplate.Manage.superclass.constructor.call(this, cfg);
        // this.county(null);
    }
});
