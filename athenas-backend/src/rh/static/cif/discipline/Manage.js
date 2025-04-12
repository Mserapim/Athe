/**
 *
 **/
Ext._define('cif.discipline.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getDiscipline: function() {
        if(!this.discipline) {
            this.discipline = Ext._create('cif.discipline.DisciplineGrid', {
                region: 'center',
            });
        }

        return this.discipline;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Disciplina'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getDiscipline(),
                ]
            }
        );

        cif.discipline.Manage.superclass.constructor.call(this, cfg);
    }
});
