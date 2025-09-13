"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useFieldStore } from "@/lib/store/fieldStore";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";

const fieldSchema = z.object({
  name: z.string().min(1, "Field name is required"),
  area: z.number().min(0.1, "Area must be greater than 0"),
  cropType: z.string().min(1, "Crop type is required"),
  soilType: z.string().optional(),
  irrigationType: z.string().optional(),
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
});

type FieldFormData = z.infer<typeof fieldSchema>;

interface FieldFormProps {
  onClose: () => void;
  onSuccess: () => void;
  field?: any;
}

export default function FieldForm({
  onClose,
  onSuccess,
  field,
}: FieldFormProps) {
  const { addField, updateField, isLoading } = useFieldStore();
  const isEditing = !!field;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FieldFormData>({
    resolver: zodResolver(fieldSchema),
    defaultValues: field || {
      latitude: 28.6139, // Default to Delhi
      longitude: 77.209,
    },
  });

  const onSubmit = async (data: FieldFormData) => {
    try {
      if (isEditing) {
        await updateField(field.id, data);
      } else {
        await addField(data);
      }
      onSuccess();
    } catch (error) {
      console.error("Failed to save field:", error);
    }
  };

  const cropTypes = [
    "wheat",
    "rice",
    "corn",
    "sugarcane",
    "cotton",
    "soybean",
    "potato",
    "tomato",
    "onion",
    "cabbage",
    "cauliflower",
  ];

  const soilTypes = [
    "alluvial",
    "black",
    "red",
    "laterite",
    "desert",
    "mountain",
  ];

  const irrigationTypes = ["drip", "sprinkler", "flood", "furrow", "none"];

  return (
    <Modal
      isOpen
      onClose={onClose}
      title={isEditing ? "Edit Field" : "Add New Field"}
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Field Name"
            {...register("name")}
            error={errors.name?.message}
            placeholder="e.g., North Field"
          />

          <Input
            label="Area (acres)"
            type="number"
            step="0.1"
            {...register("area", { valueAsNumber: true })}
            error={errors.area?.message}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Crop Type
            </label>
            <select
              {...register("cropType")}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="">Select crop type</option>
              {cropTypes.map((crop) => (
                <option key={crop} value={crop} className="capitalize">
                  {crop}
                </option>
              ))}
            </select>
            {errors.cropType && (
              <p className="mt-1 text-sm text-red-600">
                {errors.cropType.message}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Soil Type
            </label>
            <select
              {...register("soilType")}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="">Select soil type</option>
              {soilTypes.map((soil) => (
                <option key={soil} value={soil} className="capitalize">
                  {soil}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Irrigation Type
          </label>
          <select
            {...register("irrigationType")}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="">Select irrigation type</option>
            {irrigationTypes.map((type) => (
              <option key={type} value={type} className="capitalize">
                {type}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Latitude"
            type="number"
            step="0.000001"
            {...register("latitude", { valueAsNumber: true })}
            error={errors.latitude?.message}
          />

          <Input
            label="Longitude"
            type="number"
            step="0.000001"
            {...register("longitude", { valueAsNumber: true })}
            error={errors.longitude?.message}
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button variant="outline" onClick={onClose} type="button">
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {isEditing ? "Update Field" : "Add Field"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
