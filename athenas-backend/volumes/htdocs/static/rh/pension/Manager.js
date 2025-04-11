
Ext._define('rh.pension.Manager', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
		{
			this._grid = Ext._create('rh.pension.Grid', {
				region: 'center'
			});

			// this._grid.getSelectionModel().on({
   //              scope: this,
   //              rowselect: function(selectionModel, index, record) {
   //      			this.getEventsPanel().enable();
   //                  if(record.get('kind') == 'death-pension')
   //                  {
   //                      this.getFoodPensionEventsGrid().hide();
   //                      this.getDeathPensionEventsGrid().show();
   //                      this.getDeathPensionEventsGrid().setFilterProperty('pensao_morte', record.get('pk'));
   //                      this.getDeathPensionEventsGrid().setParam('pensao_morte', record.get('pk'));
   //                      this.getDeathPensionEventsGrid().setFormValues({
   //                          pensao_morte: record.get('pk'),
   //                          pensao_morte_unicode: record.get('pensionista_unicode')
   //                      });
   //          		}
   //          		else
   //          		{
   //          			this.getDeathPensionEventsGrid().hide();
   //          			this.getFoodPensionEventsGrid().show();
   //          			this.getFoodPensionEventsGrid().setFilterProperty('pensao_alimenticia', record.get('pk'));
   //          			this.getFoodPensionEventsGrid().setParam('pensao_alimenticia', record.get('pk'));
   //                      this.getFoodPensionEventsGrid().setFormValues({
   //                          pensao_alimenticia: record.get('pk'),
   //                          pensao_alimenticia_unicode: record.get('pensionista_unicode')
   //                      });
   //          		}
   //              },
   //              rowdeselect: function(selectionModel, index, record)
   //              {
   //                  this.getFoodPensionEventsGrid().hide();
   //                  this.getDeathPensionEventsGrid().hide();
   //              }
   //          });
		}

		return this._grid;
	},

	getDeathPensionEventsGrid: function(values)
	{
		if(!this._deathPensionEventsGrid)
		{
			this._deathPensionEventsGrid = Ext._create('rh.pension.DeathPensionEventGrid', {
				title: 'Eventos de pensão por morte',
                gridAutoLoad: false,
                height: 340,
                hidden: true,
            });
		}
		return this._deathPensionEventsGrid;
	},

	getFoodPensionEventsGrid: function()
	{
		if(!this._foodPensionEventsGrid)
		{
			this._foodPensionEventsGrid = Ext._create('rh.pension.FoodPensionEventGrid', {
				title: 'Eventos de pensão alimentícia',
                gridAutoLoad: false,
                height: 340,
                hidden: true,
            });
		}
		return this._foodPensionEventsGrid;
	},

	getEventsPanel: function()
	{
		if(!this._eventsPanel)
		{
			this._eventsPanel = Ext._create('Ext.Panel', {
                id: 'rh.pension.Manager.EventsPanel',
				region: 'south',
				height: 350,
				disabled: true,
				border: false,
				items: [
					this.getFoodPensionEventsGrid(),
					this.getDeathPensionEventsGrid()
				]
			});
		}
		return this._eventsPanel;
	},


	constructor: function(cfg) {
		cfg = cfg || {};

		Ext.applyIf(
			cfg, {title: 'Gestor de Pensões'}
		);

		Ext.apply(cfg, {
			layout: 'border',
			items: [
				this.getGrid(),
				// this.getEventsPanel()
			]
		});

		rh.pension.Manager.superclass.constructor.call(this, cfg);
	}
});
