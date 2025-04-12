/**
 *
 **/
Ext._define('judicial.TriageManage', {
    extend: 'judicial.Manage',

    getOutCourtLawsuitGrid: function() {
        if(!this._outCourtLawsuitGrid) {
            this._outCourtLawsuitGrid = Ext._create('judicial.TriageOutCourtLawsuitGrid', {
                title: 'Principal',
                gridAutoLoad: false,
                columnAction: false
            });

            this._outCourtLawsuitGrid.setFilterProperty('attached_lawsuit', null, 1001, false);
            this._outCourtLawsuitGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();

                    if(selection.length > 0)
                        this.lawsuit(selection[0].get('pk'));
                    else
                        this.lawsuit(null);
                }
            });
        }

        return this._outCourtLawsuitGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                hiddenReportAction: true,
                title: 'Procedimentos Cartório'
            }
        );

        judicial.TriageManage.superclass.constructor.call(this, cfg);
    }
});
