Ext._define('rh.pvf.absence.politicalactivity.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getPoliticalActivityAbsenceGrid: function() {
        if(!this._grid) {
            this._grid = Ext._create('rh.pvf.absence.politicalactivity.Grid', {
                region: 'center',
                gridAutoLoad: false
            });
        }

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Licença para Atividade Política'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getPoliticalActivityAbsenceGrid(),
                ]
            }
        );

        rh.pvf.absence.politicalactivity.Manage.superclass.constructor.call(this, cfg);
    }
});

