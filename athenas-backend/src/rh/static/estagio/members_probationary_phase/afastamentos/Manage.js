Ext._define('estagio.members_probationary_phase.afastamentos.Manage', {
	extend: 'toolkit.widget.TabPanel',

	event: function (value, dispatch) {
		dispatch = core.nullValue(dispatch, true);
	},

	getGrid: function (cfg) {

		if (!this._eventGrid) {
			this._eventGrid = Ext._create('estagio.members_probationary_phase.afastamentos.Grid', {
				region: 'center',
			});

			this._eventGrid.getSelectionModel().on({
				scope: this,
				beforerowselect: function (eventGrid) {
					return true
				},
				rowselect: function (eventGrid, index, record) {
					this.event(record.data);
				},
				rowdeselect: function (eventGrid, index, record) {
					this.event(null);
				},
			});

			this._eventGrid.getStore().on({
				scope: this,
				beforeload: function (st, options) {
					rec = this._eventGrid.getSelectionModel().getSelected();
					this._eventGrid._lastEvent = rec ? rec.data.pk : null;
				},
				load: function (st, records, options) {
					if (!records.length)
						this.event(null);
				}
			});
		}

		return this._eventGrid;
	},

	constructor: function (cfg) {


		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
				title: 'Afastamentos'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				defaults: {
					split: true,
				},
				items: [
					this.getGrid(cfg),
				]
			}
		);

		estagio.members_probationary_phase.afastamentos.Manage.superclass.constructor.call(this, cfg);
	}
});
