/**
 *
 **/

Ext._define('rh.employee.workplace.exercisesmorethanone.Manager', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Locais com mais de 1 exercício'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items:  Ext._create('rh.employee.workplace.exercisesmorethanone.ManagerPanel', {departament: cfg.departament})
            }
        );

        rh.employee.workplace.exercisesmorethanone.Manager.superclass.constructor.call(this, cfg);
    }
});
