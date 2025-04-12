/**
 *
 **/

Ext._define('rh.publicacao.PublicationGeneralManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid) {
			var bodyWidth = Ext.getBody().getBox().width;
			var keywordFieldWidth;

			if(bodyWidth < 1440)
				keywordFieldWidth = (bodyWidth - 1060);
			else
				keywordFieldWidth = (bodyWidth - 1255);

			this._grid = Ext._create('rh.publicacao.PublicationGeneralGrid', {
				region: 'center',
				columnAction: false,
				toolbarHideLabel: (bodyWidth < 1440),
				keywordFieldWidth: keywordFieldWidth
			});

			this._grid.getSelectionModel().on({
				scope: this,
				selectionchange: function(sel) {
					var selection = sel.getSelections();

					if(selection.length > 0)
						this.publication(selection[0]);
					else
						this.publication(null);
				}
			});
		}

		return this._grid;
	},

	publication: function(value, dispatch) {
	    dispatch = (dispatch === undefined ? true : dispatch);

	    if(value !== undefined) {
	        this._publication = value;

	        if(dispatch)
	            this.observePublication();
	    }

	    return this._publication;
	},

	renderInstance: function(instance) {
		var tpl = new Ext.XTemplate(
			'{formated_content}',
			'<div class="papper seal">',
				'<div class="field small-bottom">',
					'<div class="column-two">',
						'<div class="label">Data da Expedição :</div>',
						'<div class="value">{data_expedicao}</div>',
					'</div>',
					'<div>',
						'<div class="label">Data da Vigência :</div>',
						'<div class="value">{data_vigencia}</div>',
					'</div>',
				'</div>',
				'<div class="field small-bottom">',
					'<div class="column-two">',
						'<div class="label">Data da Públicação :</div>',
						'<div class="value">{data_publicacao}</div>',
					'</div>',
					'<div>',
						'<div class="label">Página no diário :</div>',
						'<div class="value">{vehicle_page}</div>',
					'</div>',
				'</div>',
				'<div class="field small-bottom">',
					'<div class="label">Veículo de Públicação :</div>',
					'<div class="value">{veiculo_publicacao_display}</div>',
				'</div>',
			'</div>'
		);

		function prepare(instance) {
			var obj = {}

			Ext.apply(
				obj,
				instance
			)

			obj.data_expedicao = Ext.util.Format.date(obj.data_expedicao, 'd/m/Y');
			obj.data_vigencia = Ext.util.Format.date(obj.data_vigencia, 'd/m/Y');

			if(obj.data_publicacao)
				obj.data_publicacao = Ext.util.Format.date(obj.data_publicacao, 'd/m/Y');
			else
				obj.data_publicacao = 'Documento ainda não foi publicado';

			if(!obj.veiculo_publicacao)
				obj.veiculo_publicacao_display = 'Sem veículo informado';

			if(!obj.vehicle_page)
				obj.vehicle_page = 'Documento ainda não foi publicado';

			return obj;
		}

		return tpl.apply(prepare(instance));
	},

	observePublication: function() {
	    value = this.publication();

	    if(value) {
			this.getTilePagePanel().enable();
			this.getTilePagePanel().setPageContent(
				this.renderInstance(value.data)
			);

			// if(value.data.document)
			// 	this.getTilePagePanel().addPageContent(
			// 		value.data.document
			// 	);
	    }
	    else {
			this.getTilePagePanel().disable();
			this.getTilePagePanel().setPageContent('');
	    }
	},

	getTilePagePanel: function() {
	    if(!this._tilePagePanel)
	        this._tilePagePanel = Ext._create('core.TilePagePanel', {
				region: 'east',
				width: 850,
				minWidth: 850,
				maxWidth: 900,
				split: true
			});

	    return this._tilePagePanel;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Publicações'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					this.getGrid(),
					this.getTilePagePanel()
				]
			}
		);

		rh.publicacao.PublicationGeneralManage.superclass.constructor.call(this, cfg);
		this.observePublication();
	}
});
