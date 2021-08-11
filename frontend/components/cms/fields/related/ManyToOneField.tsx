import { ManyToOneFieldProps } from "@/components/cms/fields/types";
import { TableHead, useTheme } from "@material-ui/core";
import IconButton from "@material-ui/core/IconButton";
import Paper from "@material-ui/core/Paper";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableFooter from "@material-ui/core/TableFooter";
import TablePagination from "@material-ui/core/TablePagination";
import TableRow from "@material-ui/core/TableRow";
import FirstPageIcon from "@material-ui/icons/FirstPage";
import LastPageIcon from "@material-ui/icons/LastPage";
import React, { FC, useState } from "react";

interface TablePaginationActionsProps {
  count: number;
  page: number;
  rowsPerPage: number;
  onPageChange: (event: React.MouseEvent<HTMLButtonElement>, newPage: number) => void;
}

function TablePaginationActions(props: TablePaginationActionsProps) {
  const theme = useTheme();

  const { count, page, rowsPerPage, onPageChange } = props;

  const handleFirstPageButtonClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    onPageChange(event, 0);
  };

  const handleBackButtonClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    onPageChange(event, page - 1);
  };

  const handleNextButtonClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    onPageChange(event, page + 1);
  };

  const handleLastPageButtonClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    onPageChange(event, Math.max(0, Math.ceil(count / rowsPerPage) - 1));
  };

  return (
    <div>
      <IconButton
        onClick={handleLastPageButtonClick}
        disabled={page >= Math.ceil(count / rowsPerPage) - 1}
        aria-label="last page"
      >
        {theme.direction === "rtl" ? <FirstPageIcon /> : <LastPageIcon />}
      </IconButton>
    </div>
  );
}

const ManyToOneField: FC<ManyToOneFieldProps> = (props: ManyToOneFieldProps) => {
  console.log(">>>", props.name, props.object[props.name]);
  const [relatedObjects, setRelatedObjects] = useState(props.object[props.name] || []);
  console.log(relatedObjects);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const emptyRows = rowsPerPage - Math.min(rowsPerPage, relatedObjects.length - page * rowsPerPage);

  const handleChangePage = (event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <div>
      <label>{props.verboseName}</label>
      <TableContainer component={Paper}>
        <Table>
          {!!relatedObjects?.length && (
            <>
              <TableHead>
                <TableRow>
                  {relatedObjects[0].keys().map((fieldName) => (
                    <TableCell component="th" key={fieldName}>
                      {fieldName}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {(rowsPerPage > 0
                  ? relatedObjects.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  : relatedObjects
                ).map((relatedObject) => (
                  <TableRow key={relatedObject.name}>
                    {relatedObject.entries().map((fieldName, fieldValue) => (
                      <TableCell key={fieldName}>{fieldValue}</TableCell>
                    ))}
                  </TableRow>
                ))}
                {emptyRows > 0 && (
                  <TableRow>
                    <TableCell colSpan={6} />
                  </TableRow>
                )}
              </TableBody>
            </>
          )}
          <TableFooter>
            <TableRow>
              <TablePagination
                rowsPerPageOptions={[5, 10, 25, { label: "All", value: -1 }]}
                colSpan={3}
                count={relatedObjects.length}
                rowsPerPage={rowsPerPage}
                page={page}
                SelectProps={{
                  inputProps: { "aria-label": "rows per page" },
                  native: true,
                }}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
                ActionsComponent={TablePaginationActions}
              />
            </TableRow>
          </TableFooter>
        </Table>
      </TableContainer>
    </div>
  );
};

export default ManyToOneField;

{
  /* <div 
    class="js-inline-admin-formset inline-group" 
    id="{{ inline_admin_formset.formset.prefix }}-group"
    data-inline-type="tabular"
    data-inline-formset="{{ inline_admin_formset.inline_formset_data }}"
>
    <div class="tabular inline-related {% if forloop.last %}last-related{% endif %}">
        {{ inline_admin_formset.formset.management_form }}
        <fieldset class="module {{ inline_admin_formset.classes }}">
            <h2>{{ inline_admin_formset.opts.verbose_name_plural|capfirst }}</h2>
            {{ inline_admin_formset.formset.non_form_errors }}
            <table>
                <thead>
                    <tr>
                        <th class="original"></th>
                        {% for field in inline_admin_formset.fields %}
                        {% if not field.widget.is_hidden %}
                        <th class="column-{{ field.name }}{% if field.required %} required{% endif %}">{{ field.label|capfirst }}
         {% if field.help_text %}<img src="{% static "admin/img/icon-unknown.svg" %}" class="help help-tooltip" width="10" height="10" alt="({{ field.help_text|striptags }})" title="{{ field.help_text|striptags }}">{% endif %}
         </th>
       {% endif %}
     {% endfor %}
     {% if inline_admin_formset.formset.can_delete and inline_admin_formset.has_delete_permission %}<th>{% translate "Delete?" %}</th>{% endif %}
     </tr></thead>

     <tbody>
     {% for inline_admin_form in inline_admin_formset %}
        {% if inline_admin_form.form.non_field_errors %}
        <tr class="row-form-errors"><td colspan="{{ inline_admin_form|cell_count }}">{{ inline_admin_form.form.non_field_errors }}</td></tr>
        {% endif %}
        <tr class="form-row {% if inline_admin_form.original or inline_admin_form.show_url %}has_original{% endif %}{% if forloop.last and inline_admin_formset.has_add_permission %} empty-form{% endif %}"
             id="{{ inline_admin_formset.formset.prefix }}-{% if not forloop.last %}{{ forloop.counter0 }}{% else %}empty{% endif %}">
        <td class="original">
          {% if inline_admin_form.original or inline_admin_form.show_url %}<p>
          {% if inline_admin_form.original %}
          {{ inline_admin_form.original }}
          {% if inline_admin_form.model_admin.show_change_link and inline_admin_form.model_admin.has_registered_model %}<a href="{% url inline_admin_form.model_admin.opts|admin_urlname:'change' inline_admin_form.original.pk|admin_urlquote %}" class="{% if inline_admin_formset.has_change_permission %}inlinechangelink{% else %}inlineviewlink{% endif %}">{% if inline_admin_formset.has_change_permission %}{% translate "Change" %}{% else %}{% translate "View" %}{% endif %}</a>{% endif %}
          {% endif %}
          {% if inline_admin_form.show_url %}<a href="{{ inline_admin_form.absolute_url }}">{% translate "View on site" %}</a>{% endif %}
            </p>{% endif %}
          {% if inline_admin_form.needs_explicit_pk_field %}{{ inline_admin_form.pk_field.field }}{% endif %}
          {% if inline_admin_form.fk_field %}{{ inline_admin_form.fk_field.field }}{% endif %}
          {% spaceless %}
          {% for fieldset in inline_admin_form %}
            {% for line in fieldset %}
              {% for field in line %}
                {% if not field.is_readonly and field.field.is_hidden %}{{ field.field }}{% endif %}
              {% endfor %}
            {% endfor %}
          {% endfor %}
          {% endspaceless %}
        </td>
        {% for fieldset in inline_admin_form %}
          {% for line in fieldset %}
            {% for field in line %}
              {% if field.is_readonly or not field.field.is_hidden %}
              <td{% if field.field.name %} class="field-{{ field.field.name }}"{% endif %}>
              {% if field.is_readonly %}
                  <p>{{ field.contents }}</p>
              {% else %}
                  {{ field.field.errors.as_ul }}
                  {{ field.field }}
              {% endif %}
              </td>
              {% endif %}
            {% endfor %}
          {% endfor %}
        {% endfor %}
        {% if inline_admin_formset.formset.can_delete and inline_admin_formset.has_delete_permission %}
          <td class="delete">{% if inline_admin_form.original %}{{ inline_admin_form.deletion_field.field }}{% endif %}</td>
        {% endif %}
        </tr>
     {% endfor %}
     </tbody>
   </table>
</fieldset>
  </div>
</div> */
}
