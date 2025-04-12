Ext._define('corregedoria.cirdir.evaluator.Manage', {
  extend: 'toolkit.widget.TabPanel',

    getEvaluatorGrid: function(cfg) {
        if(!this._evaluatorGrid) {
            this._evaluatorGrid = Ext._create('corregedoria.cirdir.evaluator.Grid', {
                region: 'center',
            });
        }
        return this._evaluatorGrid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};
        Ext.applyIf(
            cfg,
            {
                title: 'Avaliadores'
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getEvaluatorGrid(cfg)
                ],
            }
        );
        corregedoria.cirdir.evaluator.Manage.superclass.constructor.call(this, cfg);

    },
});
